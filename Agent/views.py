from django.shortcuts import render

from Agent.models import Agent
from Agent.models import Client
from Agent.models import Step
from Agent.serializers import AgentSerializer
from Agent.serializers import ClientSerializer
from Agent.serializers import StepSerializer

from . import permissions

from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

import logging

import requests
from oauth2_provider.contrib.rest_framework import OAuth2Authentication

from django.conf import settings


## Standard errors
agentDNE = {'code': 0, 'message': 'No agent exists with this email address.'}
agentBadPassword = {'code': 1, 'message': 'Incorrect password.'}
agentTempPassword = {'code': 2, 'message': 'Agent has temporary password. Must change password immediately.'}

class AgentsList(APIView):
    serializer_class = AgentSerializer
    permission_classes = (AllowAny,)

    def get(self, request):
        agents = Agent.objects.all()
        serializer = AgentSerializer(agents, many=True)
        return Response(serializer.data)



class AgentRegister(APIView):
    """
    Register a new user.
    """
    serializer_class = AgentSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        print("hi")
        if serializer.is_valid():
            serializer.save()
            print("bye")
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        print("sup")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AgentLogin(APIView):
    """API to login agent"""

    def post(self, request):
        """
        :param mls_id:  mls id for agent
        :param region_id: region id for agent
        :param password: password entered by agent
        :return access token if login successful else error message:
        """

        logger = logging.getLogger('django')

        logger.setLevel(logging.DEBUG)
        logger.info('Login Flow Initiated')

        email = request.data.get('email')
        password = request.data.get('password')
        try:
            mls_agent = Agent.objects.get(email=email)
        except Exception as e:
            return Response(agentDNE, status=status.HTTP_404_NOT_FOUND)
            
        is_password_correct = mls_agent.check_password(password)
        print(is_password_correct)
        if not is_password_correct:
            return Response(agentBadPassword, status=status.HTTP_400_BAD_REQUEST)
        ## Check if user has a temporary password
        if mls_agent.temp_password:
            ## Redirect to change password view
            return Response(agentTempPassword, status=status.HTTP_400_BAD_REQUEST)
        auth = (settings.OAUTH2_CLIENT_ID_AGENTS,
                settings.OAUTH2_CLIENT_SECRET_AGENTS)
        print(auth)
        auth_response = requests.post(settings.REDIRECT_URL + 'o/token/',
                                 data={'username': mls_agent.email, 'password': password, 'grant_type': 'password'},
                                 auth=auth)
        print(auth_response.json())
        if auth_response.ok:
            print("here")
            return Response(auth_response.json(), status=status.HTTP_200_OK)

        return Response("nah fam",
                        status=status.HTTP_400_BAD_REQUEST)

class AgentChangePassword(APIView):
    """ API to change password of Agent """

    def post(self, request):
        """
        :param email: email address of agent
        :param current_password: current/temporary password
        :param new_password: new password to set
        :return result of password change
        """

        mls_agent = Agent.objects.get(email=request.data.get('email'))
        
        if not mls_agent:
            return Response("not agent", status=status.HTTP_404_NOT_FOUND)

        is_password_correct = mls_agent.check_password(request.data.get('current_password'))

        if not is_password_correct:
            return Response("Incorrect password", status=status.HTTP_400_BAD_REQUEST)

        ## Set new password
        result = mls_agent.set_new_password(request.data.get('new_password'))

        if result:
            return Response("successfully changed password", status=status.HTTP_200_OK)

        return Response("error", status=status.HTTP_400_BAD_REQUEST)
        

class AgentForgotPassword(APIView):
    """ API to recover password """

    def post(self, request):
        """
        :param email:  email for agent account
        :return success message if reset complete else error message:
        """

        email = request.data.get('email')
        mls_agent = Agent.objects.get(email=email)
        if not mls_agent:
            return Response(agentDNE, status=status.HTTP_404_NOT_FOUND)

        ## Reset password
        result = mls_agent.reset_password()

        if result:
            return Response("successfully reset password", status=status.HTTP_200_OK)
        else:
            return Response("error", status=status.HTTP_400_BAD_REQUEST)

class SingleAgent(APIView):

    def get(self, request):
        mls_region = request.GET.get('mls_region')
        mls_id = request.GET.get('mls_id')

        try:
            agent = Agent.objects.get(mls_region=mls_region, mls_id=mls_id)
            agent_name = agent.first_name
            print(agent_name)
            serializer = AgentSerializer(agent)
            print(serializer.data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Agent.DoesNotExist:
            return Response("Not an Agent", status=status.HTTP_400_BAD_REQUEST)


class SingleClient(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = [OAuth2Authentication]

    def get(self, request):
        agent = request.user
        email = request.GET.get('email')
        client_type = request.GET.get('client_type')
        try:
            client = agent.client_set.filter(email=email, client_type=client_type)
            print(client.first_name)
            serializer = ClientSerializer(client)
            print(serializer.data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            return Response("Not a Client", status=status.HTTP_400_BAD_REQUEST)


    def post(self, request):
        serializer = ClientSerializer(data=request.data)

        if serializer.is_valid():
            email = request.data.get('email')
            first_name = request.data.get('first_name')
            last_name = request.data.get('last_name')
            phone_number = request.data.get('phone_number')
            client_type = request.data.get('client_type')
            address = request.data.get('address')
            city = request.data.get('city')
            state = request.data.get('state')
            zipcode = request.data.get('zipcode')
            est_price = request.data.get('est_price')
            commission = request.data.get('commission')
            agent = request.user
            print(agent)
            client = agent.client_set.filter(email=email, client_type=client_type)
            print(client)
            if client:
                return Response("Already a Client", status=status.HTTP_400_BAD_REQUEST)

            c = Client(email=email, first_name=first_name, last_name=last_name, phone_number=phone_number,
                       client_type = client_type, address=address, city=city, state=state, zipcode=zipcode, est_price=est_price,
                       commission=commission, agent=agent)
            c.save()

            if(client_type == 'B'):
                step_one = Step(client=c, ordering=1, name="Step One", complete=False)
                step_two = Step(client=c, ordering=1, name="Step Two", complete=False)
                step_three = Step(client=c, ordering=1, name="Step Three", complete=False)
                step_four = Step(client=c, ordering=1, name="Step Four", complete=False)
                step_five = Step(client=c, ordering=1, name="Step Five", complete=False)
                step_one.save()
                step_two.save()
                step_three.save()
                step_four.save()
                step_five.save()
            else:
                step_one = Step(client=c, ordering=1, name="Step OneS", complete=False)
                step_two = Step(client=c, ordering=1, name="Step TwoS", complete=False)
                step_three = Step(client=c, ordering=1, name="Step ThreeS", complete=False)
                step_four = Step(client=c, ordering=1, name="Step FourS", complete=False)
                step_five = Step(client=c, ordering=1, name="Step FiveS", complete=False)
                step_one.save()
                step_two.save()
                step_three.save()
                step_four.save()
                step_five.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)


class ClientSteps(APIView):

    def get(self, request):
        agent = request.user
        email = request.GET.get('email')
        client_type = request.GET.get('client_type')

        try:
            client = agent.client_set.filter(email=email, client_type=client_type)
        except:
            return Response("Not a Client", status=status.HTTP_400_BAD_REQUEST)

        steps = client.step_set.all()

        serializer = StepSerializer(steps, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class UpdateStep(APIView):

    def post(self, request):
        serializer = ClientSerializer(data=request.data)




class RemoveClient(APIView):

    def post(self, request):
        agent = request.user
        email = request.GET.get('email')
        client_type = request.GET.get('client_type')

        try:
            client = agent.client_set.filter(email=email, client_type=client_type)
            client.delete()
            return Response("Client deleted", status=status.HTTP_200_OK)
        except:
            return Response("Not a Client", status=status.HTTP_400_BAD_REQUEST)





class ClientList(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = [OAuth2Authentication]

    def get(self, request):
        agent = request.user
        client_type = request.GET.get('client_type')
        clients = {}
        email = agent.email
        # clients = agent.client_set.all()
        if(client_type == 'B'):
            clients = agent.client_set.filter(client_type=client_type)
        elif(client_type == 'S'):
            clients = agent.client_set.filter(client_type=client_type)

        serializer = ClientSerializer(clients, many=True, context={'user': request.user})
        return Response(serializer.data, status=status.HTTP_200_OK)



class AgentClientList(APIView):

    def get(self, request):
        mls_region = request.GET.get('mls_region')
        mls_id = request.GET.get('mls_id')

        try:
            agent = Agent.objects.get(mls_region=mls_region, mls_id=mls_id)
        except Agent.DoesNotExist:
            return Response("ay", status=status.HTTP_400_BAD_REQUEST)

        clients = agent.clients
        serializer = ClientSerializer(clients, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        mls_region = request.data.get('agent_mls_region')
        mls_id = request.data.get('agent_mls_id')
        email = request.data.get('email')
        client_type = request.data.get('client_type')

        serializer = ClientSerializer(data=request.data)
        # print(request.data)
        if serializer.is_valid():
            serializer.save()

        try:
            agent = Agent.objects.get(mls_region=mls_region, mls_id=mls_id)
        except Agent.DoesNotExist:
            return Response("tru", status=status.HTTP_400_BAD_REQUEST)

        client = Client.objects.get(agent_mls_region=mls_region, agent_mls_id=mls_id, email=email, client_type=client_type)

        agent.clients.add(client)
        agent.save()
        s = AgentSerializer(agent)

        return Response(s.data, status=status.HTTP_200_OK)






