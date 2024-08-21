from typing import List

from fastapi import APIRouter, HTTPException
from db.automation import Automation, AutomationNode, ConditionEdge, Condition, Location
import models as api_models

router = APIRouter()


@router.post("/")
async def create_automation(automation: api_models.AutomationRequest) -> api_models.AutomationResponse:
    try:
        new_automation = Automation(name=automation.name)
        new_automation.save()
        return api_models.AutomationResponse.from_orm(new_automation)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/")
async def get_automations() -> List[api_models.AutomationResponse]:
    automations = Automation.objects()
    return [api_models.AutomationResponse.from_orm(automation) for automation in automations]


@router.get("/{automation_id}")
async def read_automation(automation_id: str) -> api_models.AutomationResponse:
    automation = Automation.objects(id=automation_id).first()
    if automation:
        return api_models.AutomationResponse.from_orm(automation)
    raise HTTPException(status_code=404, detail="Automation not found")


@router.put("/{automation_id}")
async def update_automation(automation_id: str,
                            automation: api_models.AutomationUpdateRequest) -> api_models.AutomationResponse:
    db_automation = Automation.objects(id=automation_id).first()
    if db_automation:
        db_automation.name = automation.name
        db_automation.is_active = automation.is_active
        db_automation.save()
        return api_models.AutomationResponse.from_orm(db_automation)
    raise HTTPException(status_code=404, detail="Automation not found")


@router.delete("/{automation_id}")
async def delete_automation(automation_id: str) -> api_models.AutomationResponse:
    automation = Automation.objects(id=automation_id).first()
    if automation:
        automation.delete()
        return api_models.AutomationResponse.from_orm(automation)
    raise HTTPException(status_code=404, detail="Automation not found")


@router.post("/{automation_id}/nodes/")
async def create_node(automation_id: str, node: api_models.AutomationNodeRequest) -> api_models.AutomationNodeResponse:
    automation = Automation.objects(id=automation_id).first()
    if not automation:
        raise HTTPException(status_code=404, detail="Automation not found")

    new_node = AutomationNode(smart_controller_id=node.smart_controller_id, action_id=node.action_id,
                              unique_key=f"{automation_id};{node.smart_controller_id};{node.action_id}",
                              location=Location(x=node.location.x, y=node.location.y))
    new_node.save()
    automation.add_node(new_node)
    return api_models.AutomationNodeResponse.from_orm(new_node)


@router.get("/{automation_id}/nodes/{node_id}")
async def read_node(automation_id: str, node_id: str) -> api_models.AutomationNodeResponse:
    automation = Automation.objects(id=automation_id).first()
    if not automation:
        raise HTTPException(status_code=404, detail="Automation not found")

    node = AutomationNode.objects(unique_key=node_id).first()
    if node and node in automation.nodes:
        return api_models.AutomationNodeResponse.from_orm(node)
    raise HTTPException(status_code=404, detail="Node not found")


@router.get("/{automation_id}/nodes/")
async def read_automations_nodes(automation_id: str) -> List[api_models.AutomationNodeResponse]:
    automation = Automation.objects(id=automation_id).first()
    if not automation:
        raise HTTPException(status_code=404, detail="Automation not found")

    return [api_models.AutomationNodeResponse.from_orm(node) for node in automation.nodes]


@router.put("/{automation_id}/nodes")
async def update_node(automation_id: str,
                      node: api_models.AutomationNodeUpdateRequest) -> api_models.AutomationNodeResponse:
    automation = Automation.objects(id=automation_id).first()
    if not automation:
        raise HTTPException(status_code=404, detail="Automation not found")

    db_node = AutomationNode.objects(unique_key=f"{automation_id};{node.smart_controller_id};{node.action_id}").first()
    if db_node and db_node in automation.nodes:
        db_node.smart_controller_id = node.smart_controller_id
        db_node.action_id = node.action_id
        db_node.location = Location(x=node.location.x, y=node.location.y)
        db_node.save()
        return api_models.AutomationNodeResponse.from_orm(db_node)
    raise HTTPException(status_code=404, detail="Node not found")


@router.delete("/{automation_id}/nodes/{unique_key}")
async def delete_node(automation_id: str, unique_key: str) -> api_models.AutomationNodeResponse:
    automation = Automation.objects(id=automation_id).first()
    if not automation:
        raise HTTPException(status_code=404, detail="Automation not found")

    node = AutomationNode.objects(unique_key=unique_key).first()
    if node and node in automation.nodes:
        automation.nodes.remove(node)
        automation.save()
        node.delete()
        return api_models.AutomationNodeResponse.from_orm(node)
    raise HTTPException(status_code=404, detail="Node not found")


@router.post("/{automation_id}/edges/")
async def create_edge(automation_id: str, edge: api_models.AutomationEdgeRequest) -> api_models.AutomationEdgeResponse:
    automation = Automation.objects(id=automation_id).first()
    if not automation:
        raise HTTPException(status_code=404, detail="Automation not found")

    source = AutomationNode.objects(id=edge.source.id).first()
    target = AutomationNode.objects(id=edge.target.id).first()
    if not source or not target:
        raise HTTPException(status_code=404, detail="Source or target node not found")

    condition = Condition(**edge.condition.dict())
    new_edge = ConditionEdge(source=source, target=target, condition=condition)
    new_edge.save()
    automation.add_edge(new_edge)
    new_edge.condition = api_models.AutomationEdgeConditionRequest.from_orm(condition)
    return api_models.AutomationEdgeResponse.from_orm(new_edge)


@router.get("/{automation_id}/edges/{edge_id}")
async def read_edge(automation_id: str, edge_id: str) -> api_models.AutomationEdgeResponse:
    automation = Automation.objects(id=automation_id).first()
    if not automation:
        raise HTTPException(status_code=404, detail="Automation not found")

    edge = ConditionEdge.objects(id=edge_id).first()
    if edge and edge in automation.edges:
        return api_models.AutomationEdgeResponse.from_orm(edge)
    raise HTTPException(status_code=404, detail="Edge not found")


@router.put("/{automation_id}/edges/{edge_id}")
async def update_edge(automation_id: str, edge_id: str,
                      edge: api_models.AutomationEdgeUpdateRequest) -> api_models.AutomationEdgeResponse:
    automation = Automation.objects(id=automation_id).first()
    if not automation:
        raise HTTPException(status_code=404, detail="Automation not found")

    db_edge = ConditionEdge.objects(id=edge_id).first()
    if db_edge and db_edge in automation.edges:
        source = AutomationNode.objects(id=edge.source_id).first()
        target = AutomationNode.objects(id=edge.target_id).first()
        if not source or not target:
            raise HTTPException(status_code=404, detail="Source or target node not found")

        db_edge.source = source
        db_edge.target = target
        db_edge.condition = Condition(**edge.condition.dict())
        db_edge.save()
        return api_models.AutomationEdgeResponse.from_orm(db_edge)
    raise HTTPException(status_code=404, detail="Edge not found")


@router.delete("/{automation_id}/edges/{edge_id}")
async def delete_edge(automation_id: str, edge_id: str) -> api_models.AutomationEdgeResponse:
    automation = Automation.objects(id=automation_id).first()
    if not automation:
        raise HTTPException(status_code=404, detail="Automation not found")

    edge = ConditionEdge.objects(id=edge_id).first()
    if edge and edge in automation.edges:
        automation.edges.remove(edge)
        automation.save()
        edge.delete()
        return api_models.AutomationEdgeResponse.from_orm(edge)
    raise HTTPException(status_code=404, detail="Edge not found")
