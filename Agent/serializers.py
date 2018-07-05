from rest_framework import serializers
from Agent.models import User
from Agent.models import Agent
from Agent.models import Client
from Agent.models import Step


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class AgentSerializer(serializers.ModelSerializer):
    user = User()

    #password = serializers.CharField(write_only=True, required=True)
    #birthday = serializers.DateField(format="%m/%d/%Y", input_formats=['%m/%d/%Y'])

    class Meta:
        model = Agent
        #fields = ('id', 'user', 'email', 'first_name', 'last_name', 'mls_region', 'mls_id', 'birthday', 'password')
        fields = ('id', 'user', 'mls_id', 'mls_region')

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
        fields = ('id', 'client', 'ordering', 'name', 'complete', 'agent_email', 'date', 'tags')

