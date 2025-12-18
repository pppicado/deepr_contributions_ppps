import asyncio
import json
import re
from typing import List, Dict, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from models import Conversation, Node, NodeType, User
from openrouter_service import OpenRouterClient

class DxOEngine:
    def __init__(self, db: AsyncSession, user: User, openrouter_client: OpenRouterClient):
        self.db = db
        self.user = user
        self.client = openrouter_client

    async def create_node(self, conversation_id: int, parent_id: Optional[int], node_type: str, content: str, model_name: str = None, metadata: Dict = None):
        node = Node(
            conversation_id=conversation_id,
            parent_id=parent_id,
            type=node_type,
            content=content,
            model_name=model_name
        )
        self.db.add(node)
        await self.db.commit()
        await self.db.refresh(node)
        return node

    async def run_dxo_pipeline(self, conversation_id: int, root_node: Node, roles: List[Dict]):
        """
        Orchestrates the DxO workflow:
        Phase A: Proposal (Lead System Architect)
        Phase B: Critique (Critical Reviewer)
        Phase C: Defense & Refinement Loop (QA Strategist + Lead Architect)
        Phase D: Convergence
        """

        # Helper to find role by name
        def get_role_model(role_name):
            for r in roles:
                if r['name'] == role_name:
                    return r['model']
            # Fallback
            return roles[0]['model'] if roles else "gpt-4o"

        def get_role_instructions(role_name):
            for r in roles:
                if r['name'] == role_name:
                    return r.get('instructions', "")
            return ""

        lead_architect_model = get_role_model("Lead Researcher") # Assuming mapped from UI "Lead Researcher" -> Lead Architect logic
        # Or better, match strictly what UI sends.
        # UI Mockup shows "Lead Researcher", "Critical Reviewer", "Domain Expert".
        # But Prompt description says: "Lead System Architect", "Critical Reviewer", "QA Strategist".
        # I should probably support flexible roles, but Identify key actors.
        # "Critical Reviewer" is mandatory.
        # "Lead Researcher" or "Lead Architect" is likely the proposer.
        # "QA Strategist" might be mapped to "Domain Expert" or implicitly added?
        # The prompt says: "The Orchestrator activates the Lead System Architect... It manages a debate between the roles you defined."
        # AND "Roles of the Agents... QA Strategist...".
        # I will assume the UI sends the roles config, and I should map them or use them.
        # If the user defines "Lead Researcher", I use that as the Proposer.
        # If "Critical Reviewer" is defined, I use that as the Critic.
        # If "Domain Expert" is defined, maybe they chime in?
        # The prompt hardcodes: Lead System Architect, Critical Reviewer, QA Strategist.
        # I should probably map the UI roles to these slots if possible, or just use the first role as Proposer, finding "Critical Reviewer" by name for Critique.

        proposer_role = next((r for r in roles if "Lead" in r['name'] or "Architect" in r['name'] or "Researcher" in r['name']), roles[0])
        critic_role = next((r for r in roles if "Critical Reviewer" in r['name']), None)
        qa_role = next((r for r in roles if "QA" in r['name'] or "Quality" in r['name']), None)

        if not critic_role:
            yield json.dumps({'type': 'error', 'message': 'Critical Reviewer role is missing!'})
            return

        # Phase A: Proposal
        yield json.dumps({'type': 'status', 'message': f'Phase A: {proposer_role["name"]} is drafting the proposal...'})

        proposal_prompt = f"""
        You are the {proposer_role['name']}.
        Instructions: {proposer_role.get('instructions', '')}

        User Request: "{root_node.content}"

        Please provide a solid initial design/response. Focus on structure, patterns, and scalability.
        """

        response = await self.client.chat_completion(
            model=proposer_role['model'],
            messages=[{"role": "user", "content": proposal_prompt}]
        )
        draft_content = response.choices[0].message.content
        draft_node = await self.create_node(conversation_id, root_node.id, "proposal", draft_content, model_name=proposer_role['model'])
        yield json.dumps({'type': 'node', 'node': {'id': draft_node.id, 'type': 'proposal', 'content': draft_node.content, 'model': draft_node.model_name}})

        # Loop
        iteration = 0
        max_iterations = 3
        confidence_score = 0

        while iteration < max_iterations and confidence_score < 85:
            iteration += 1
            yield json.dumps({'type': 'status', 'message': f'Phase B: Critical Reviewer is analyzing (Loop {iteration})...'})

            # Phase B: Critique
            critique_prompt = f"""
            You are the {critic_role['name']}.
            Instructions: {critic_role.get('instructions', 'TEAR DOWN the proposal. Scan for risks, flaws, complexity.')}

            Review the following draft:

            {draft_content}

            Output a Critique Report.
            IMPORTANT: You must include a "Confidence Score" (0-100) indicating your confidence in the design's safety and completeness.
            Format your response as JSON or clearly structured text where "Score: X" can be parsed.
            """

            response = await self.client.chat_completion(
                model=critic_role['model'],
                messages=[{"role": "user", "content": critique_prompt}]
            )
            critique_content = response.choices[0].message.content

            # Parse Score
            score_match = re.search(r'(?:Confidence )?Score:\s*(\d+)', critique_content, re.IGNORECASE)
            if score_match:
                confidence_score = int(score_match.group(1))
            else:
                # Default low if not found
                confidence_score = 0

            critique_node = await self.create_node(conversation_id, draft_node.id, "critique", critique_content, model_name=critic_role['model'])
            yield json.dumps({'type': 'node', 'node': {'id': critique_node.id, 'type': 'critique', 'content': critique_content, 'model': critique_node.model_name, 'score': confidence_score}})

            if confidence_score >= 85:
                break

            # Phase C: Refinement
            # QA Strategist (Optional if not defined, maybe Reviewer acts as one or we skip?)
            # Prompt says "QA Strategist looks at Draft_v1 and Critique. Generates test cases."
            qa_content = ""
            if qa_role:
                yield json.dumps({'type': 'status', 'message': f'Phase C: {qa_role["name"]} is generating test cases...'})
                qa_prompt = f"""
                You are the {qa_role['name']}.
                Instructions: {qa_role.get('instructions', 'Generate test cases that would prove the flaws exist.')}

                Draft:
                {draft_content}

                Critique:
                {critique_content}

                Generate test cases.
                """
                response = await self.client.chat_completion(
                    model=qa_role['model'],
                    messages=[{"role": "user", "content": qa_prompt}]
                )
                qa_content = response.choices[0].message.content
                qa_node = await self.create_node(conversation_id, critique_node.id, "test_cases", qa_content, model_name=qa_role['model'])
                yield json.dumps({'type': 'node', 'node': {'id': qa_node.id, 'type': 'test_cases', 'content': qa_content, 'model': qa_node.model_name}})

            # Rebuttal/Fix (Lead Architect)
            yield json.dumps({'type': 'status', 'message': f'Phase C: {proposer_role["name"]} is refining the design...'})

            refine_prompt = f"""
            You are the {proposer_role['name']}.
            Your previous design scored {confidence_score}%.

            Critique:
            {critique_content}

            {f"Test Cases from QA:{qa_content}" if qa_content else ""}

            Fix the issues identified. Provide a new version (Draft_v{iteration+1}).
            """

            response = await self.client.chat_completion(
                model=proposer_role['model'],
                messages=[{"role": "user", "content": refine_prompt}]
            )
            draft_content = response.choices[0].message.content
            draft_node = await self.create_node(conversation_id, critique_node.id, "refinement", draft_content, model_name=proposer_role['model'])
            yield json.dumps({'type': 'node', 'node': {'id': draft_node.id, 'type': 'refinement', 'content': draft_content, 'model': draft_node.model_name}})

        # Final Verdict
        yield json.dumps({'type': 'status', 'message': 'Finalizing result...'})
        final_verdict = f"""
        Final Output
        Status: {"APPROVED" if confidence_score >= 85 else "Review Limit Reached"} (Confidence: {confidence_score}%)
        Iterations: {iteration} Loops

        EXECUTIVE SUMMARY:
        (See final draft)
        """
        # Create a final node that points to the last draft
        final_node = await self.create_node(conversation_id, draft_node.id, "verdict", final_verdict, model_name="System")
        yield json.dumps({'type': 'node', 'node': {'id': final_node.id, 'type': 'verdict', 'content': final_verdict, 'model': 'System'}})
