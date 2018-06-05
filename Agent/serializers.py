from rest_framework import serializers
from Agent.models import Agent
from Agent.models import Client
from Agent.models import Step


class AgentSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = Agent
        fields = ('id', 'email', 'first_name', 'last_name', 'mls_region', 'mls_id', 'password')

    def create(self, validated_data):
        return Agent.objects._create_user(**validated_data)

class ClientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Client
        fields = ('id', 'email', 'first_name', 'last_name', 'phone_number', 'client_type', 'address', 'city',
                  'state', 'zipcode', 'est_price', 'commission')

class StepSerializer(serializers.ModelSerializer):
    client = serializers.CharField(source='Client.email')

    class Meta:
        model = Step
        fields = ('id', 'ordering', 'name', 'complete', 'date')

