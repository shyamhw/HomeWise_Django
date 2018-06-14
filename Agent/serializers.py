from rest_framework import serializers
from Agent.models import Agent
from Agent.models import Client
from Agent.models import Step


class AgentSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    birthday = serializers.DateField(format="%m/%d/%Y", input_formats=['%m/%d/%Y'])

    class Meta:
        model = Agent
        fields = ('id', 'email', 'first_name', 'last_name', 'mls_region', 'mls_id', 'birthday', 'password')

    def create(self, validated_data):
        return Agent.objects._create_user(**validated_data)

class ClientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Client
        fields = ('id', 'email', 'first_name', 'last_name', 'phone_number', 'client_type', 'address', 'city',
                  'state', 'zipcode', 'est_price', 'commission', 'commission_val', 'total_steps', 'steps_complete',
                  'steps_percentage')

class StepSerializer(serializers.ModelSerializer):
    client = ClientSerializer()
    date = serializers.DateField(format="%m/%d/%Y", input_formats=['%m/%d/%Y'])

    class Meta:
        model = Step
        fields = ('id', 'client', 'ordering', 'name', 'complete', 'agent_email', 'date')

