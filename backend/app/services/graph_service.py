from uuid import uuid5, NAMESPACE_URL
from ..core.config import settings

class GraphService:
    def __init__(self) -> None:
        self.enabled = settings.use_neo4j
        self.driver = None
        if self.enabled:
            try:
                from neo4j import GraphDatabase
                self.driver = GraphDatabase.driver(settings.neo4j_uri, auth=(settings.neo4j_user, settings.neo4j_password))
            except Exception:
                # Keep API usable while surfacing graph errors through node/edge counts.
                self.driver = None

    def build_from_rules(self, document: dict, chunks: list[dict], rules: list[dict]) -> tuple[int, int]:
        if not self.driver:
            return 0, 0
        node_count = 0
        edge_count = 0
        with self.driver.session() as session:
            session.execute_write(self._upsert_document, document)
            node_count += 1
            for chunk in chunks:
                session.execute_write(self._upsert_chunk, document, chunk)
                node_count += 1
                edge_count += 1
            for rule in rules:
                created = session.execute_write(self._upsert_rule_graph, rule)
                node_count += created[0]
                edge_count += created[1]
        return node_count, edge_count

    def get_graph(self) -> dict:
        if not self.driver:
            return {"nodes": [], "edges": []}
        with self.driver.session() as session:
            records = session.run("""
                MATCH (n)
                OPTIONAL MATCH (n)-[r]->(m)
                RETURN n, r, m
                LIMIT 300
            """)
            nodes = {}
            edges = []
            for record in records:
                for key in ["n", "m"]:
                    node = record.get(key)
                    if node:
                        nodes[str(node.element_id)] = {
                            "id": str(node.element_id),
                            "label": node.get("label", next(iter(node.labels), "Node")),
                            "type": next(iter(node.labels), "Node"),
                            "properties": dict(node),
                        }
                rel = record.get("r")
                m = record.get("m")
                n = record.get("n")
                if rel and n and m:
                    edges.append({
                        "id": str(rel.element_id),
                        "source_id": str(n.element_id),
                        "target_id": str(m.element_id),
                        "relationship": rel.type,
                        "properties": dict(rel),
                    })
            return {"nodes": list(nodes.values()), "edges": edges}

    def related_context(self, procedure: str | None, limit: int = 6) -> list[dict]:
        if not self.driver or not procedure:
            return []
        with self.driver.session() as session:
            records = session.run("""
                MATCH (p:Procedure)-[r]-(n)
                WHERE toLower(p.name) CONTAINS toLower($procedure)
                RETURN p.name AS procedure, type(r) AS relationship, labels(n)[0] AS node_type, n.label AS label, n.text AS text
                LIMIT $limit
            """, procedure=procedure, limit=limit)
            return [dict(record) for record in records]

    @staticmethod
    def _node_id(node_type: str, value: str) -> str:
        return str(uuid5(NAMESPACE_URL, f"{node_type}:{value}"))

    @staticmethod
    def _upsert_document(tx, document):
        tx.run("""
            MERGE (d:Document {id:$id})
            SET d.label=$file_name, d.storage_uri=$storage_uri
        """, id=document["id"], file_name=document["file_name"], storage_uri=document["storage_uri"])

    @staticmethod
    def _upsert_chunk(tx, document, chunk):
        tx.run("""
            MERGE (c:Chunk {id:$id})
            SET c.label=$label, c.page_number=$page_number, c.text=$text
            WITH c
            MATCH (d:Document {id:$document_id})
            MERGE (d)-[:HAS_CHUNK]->(c)
        """, id=chunk["id"], label=f"Page {chunk['page_number']} Chunk {chunk['chunk_index']}", page_number=chunk["page_number"], text=chunk["text"][:1000], document_id=document["id"])

    @staticmethod
    def _upsert_rule_graph(tx, rule):
        node_count = 0
        edge_count = 0
        chunk_id = rule["chunk_id"]
        if rule.get("procedure"):
            tx.run("""
                MERGE (p:Procedure {name:$procedure})
                SET p.label=$procedure
                WITH p
                MATCH (c:Chunk {id:$chunk_id})
                MERGE (c)-[:MENTIONS_PROCEDURE {rule_id:$rule_id}]->(p)
            """, procedure=rule["procedure"], chunk_id=chunk_id, rule_id=rule["id"])
            node_count += 1
            edge_count += 1
            if rule.get("requirement_text"):
                req_id = GraphService._node_id("requirement", rule["requirement_text"].lower())
                tx.run("""
                    MATCH (p:Procedure {name:$procedure})
                    MERGE (req:Requirement {id:$req_id})
                    SET req.label=$label, req.text=$text
                    MERGE (p)-[:REQUIRES {rule_id:$rule_id}]->(req)
                    WITH req
                    MATCH (c:Chunk {id:$chunk_id})
                    MERGE (req)-[:SUPPORTED_BY {rule_id:$rule_id}]->(c)
                """, procedure=rule["procedure"], req_id=req_id, label=rule["requirement_text"][:120], text=rule["requirement_text"], chunk_id=chunk_id, rule_id=rule["id"])
                node_count += 1
                edge_count += 2
            tx.run("""
                MATCH (p:Procedure {name:$procedure})
                MERGE (d:CoverageDecision {decision:$decision})
                SET d.label=$decision
                MERGE (p)-[:HAS_DECISION {rule_id:$rule_id}]->(d)
            """, procedure=rule["procedure"], decision=rule["decision"], rule_id=rule["id"])
            node_count += 1
            edge_count += 1
        return node_count, edge_count
