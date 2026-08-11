from typing import List


class Orchestrator:
    def route(self, query: str) -> List[str]:
        query_lower = query.lower()

        legal_keywords = [
            "legal",
            "law",
            "promotion",
            "promotional",
            "compliance",
            "restriction",
            "eligibility",
            "approved",
            "approval",
            "claim",
            "terms",
        ]

        brand_keywords = [
            "brand",
            "positioning",
            "campaign",
            "history",
            "previous",
            "past",
            "customer",
            "marketing",
        ]

        operations_keywords = [
            "vendor",
            "operations",
            "process",
            "meeting",
            "workflow",
            "onboarding",
            "delivery",
            "supplier",
        ]

        routes = []

        if any(keyword in query_lower for keyword in legal_keywords):
            routes.append("legal")

        if any(keyword in query_lower for keyword in brand_keywords):
            routes.append("brand")

        if any(keyword in query_lower for keyword in operations_keywords):
            routes.append("ops")

        if not routes:
            routes.append("brand")

        return routes
