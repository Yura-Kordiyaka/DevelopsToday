from rest_framework import viewsets, permissions
from rest_framework import status
from rest_framework.response import Response
from .models import SpyCat, Mission, Target
from .serializers import (SpyCatSerializer, MissionSerializer, TargetSerializer, SpyCatUpdateSerializer,
                          SpyCatAssignmentSerializer, TargetCompleteSerializer, TargetSerializerUpdateNote)
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError

class SpyCatViewSet(viewsets.ModelViewSet):
    queryset = SpyCat.objects.all()
    serializer_class = SpyCatSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'update' or self.action == 'partial_update':
            return SpyCatUpdateSerializer
        return SpyCatSerializer

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=True, methods=['get'])
    def get_single_cat(self, request, pk=None):
        cat = self.get_object()
        serializer = SpyCatSerializer(cat)
        return Response(serializer.data)


class MissionViewSet(viewsets.ModelViewSet):
    queryset = Mission.objects.all()
    serializer_class = MissionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=True, methods=['post'], serializer_class=SpyCatAssignmentSerializer, url_path='assign_cat')
    def assign_cat(self, request, pk=None):
        mission = self.get_object()
        cat_id = request.data.get('cat')
        try:
            cat = SpyCat.objects.get(id=cat_id)
        except SpyCat.DoesNotExist:
            return Response({"error": "Cat not found"}, status=status.HTTP_404_NOT_FOUND)

        if mission.cat is not None:
            raise ValidationError("Mission already has an assigned cat.")
        mission.cat = cat
        mission.save()
        return Response(MissionSerializer(mission).data)

    @action(detail=True, serializer_class=None, methods=['patch'])
    def complete_mission(self, request, pk=None):
        mission = self.get_object()
        mission.is_completed = True
        mission.save()
        return Response(MissionSerializer(mission).data)

    @action(detail=True, serializer_class=TargetCompleteSerializer, methods=['patch'])
    def complete_target(self, request, pk=None):
        mission = self.get_object()
        target_id = request.data.get('target_id')
        try:
            target = Target.objects.get(id=target_id, mission=mission)
        except Target.DoesNotExist:
            return Response({"error": "Target not found or does not belong to this mission"},
                            status=status.HTTP_404_NOT_FOUND)

        target.is_complete = True
        target.save()
        return Response(TargetSerializer(target).data)

    def destroy(self, request, *args, **kwargs):
        mission = self.get_object()
        if mission.cat is not None:
            raise ValidationError("Cannot delete a mission that is assigned to a cat.")
        return super().destroy(request, *args, **kwargs)


class TargetViewSet(viewsets.ModelViewSet):
    queryset = Target.objects.all()
    serializer_class = TargetSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=True, serializer_class=TargetSerializerUpdateNote, methods=['patch'])
    def update_notes(self, request, pk=None):
        target = self.get_object()
        if target.is_complete:
            raise ValidationError("Cannot modify notes after the target is complete.")
        target.notes = request.data.get('notes', target.notes)
        target.save()
        return Response(TargetSerializer(target).data)
