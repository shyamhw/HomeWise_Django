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

from datetime import datetime
import datetime as dt


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

class AgentProfile(APIView):
    serializer_class = AgentSerializer
    permission_classes = (AllowAny,)

    def get(self, request):
        agent = request.user
        serializer = AgentSerializer(agent)
        return Response(serializer.data)


class GetClient(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = [OAuth2Authentication]

    def post(self, request):
        agent = request.user
        email = request.data.get('email')
        client_type = request.data.get('client_type')

        client = agent.client_set.filter(client_type=client_type).filter(email=email)

        serializer = ClientSerializer(client, many=True)
        print(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AddClient(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = [OAuth2Authentication]


    def post(self, request):
        serializer = ClientSerializer(data=request.data)
        agent_email = request.user.email

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
            est_price = int(est_price)
            print('Est price: ' + str(est_price))
            commission = request.data.get('commission')
            commission_val = est_price * (int(commission)/100)
            print(commission_val)
            if(client_type == 'B'):
                print('bbbb')
                total_steps = 15
            else:
                print('cccc')
                total_steps = 15
            print(total_steps)
            steps_complete = 0
            print(steps_complete)
            steps_percentage = (steps_complete/total_steps) * 100
            print(steps_percentage)
            d = dt.date.today()
            today = d.strftime("%Y-%m-%d")



            agent = request.user
            print(agent)
            client = agent.client_set.filter(email=email, client_type=client_type)
            print(client)
            if client:
                return Response("Already a Client", status=status.HTTP_400_BAD_REQUEST)

            c = Client(email=email, first_name=first_name, last_name=last_name, phone_number=phone_number,
                       client_type=client_type, address=address, city=city, state=state, zipcode=zipcode, est_price=est_price,
                       commission=commission, commission_val=commission_val, total_steps=total_steps,
                       steps_complete=steps_complete, steps_percentage=steps_percentage, agent=agent)
            c.save()

            if(client_type == 'B'):
                print('hi')
                step_one = Step(client=c, ordering=1, name="Set an appointment", complete=False,
                                agent_email=agent_email, date=today)
                step_two = Step(client=c, ordering=1, name="Sign buyer’s agreement contract", complete=False,
                                agent_email=agent_email, date=today)
                step_three = Step(client=c, ordering=1, name="Set client up on MLS", complete=False,
                                  agent_email=agent_email, date=today)
                step_four = Step(client=c, ordering=1, name="Confirm mortgage pre-approval", complete=False,
                                 agent_email=agent_email, date=today)
                step_five = Step(client=c, ordering=1, name="Create buyer’s tour reports for showings", complete=False,
                                 agent_email=agent_email, date=today)
                step_six = Step(client=c, ordering=1, name="Show preferred houses to client", complete=False,
                                agent_email=agent_email, date=today)
                step_seven = Step(client=c, ordering=1, name="Create CMA report for interested properties",
                                  complete=False, agent_email=agent_email, date=today)
                step_eight = Step(client=c, ordering=1, name="Prepare offer documents", complete=False,
                                  agent_email=agent_email, date=today)
                step_nine = Step(client=c, ordering=1, name="Offer accepted", complete=False, agent_email=agent_email, date=today)
                step_ten = Step(client=c, ordering=1, name="Deposit", complete=False, agent_email=agent_email, date=today)
                step_eleven = Step(client=c, ordering=1, name="Inspections deadline", complete=False,
                                   agent_email=agent_email, date=today)
                step_twelve = Step(client=c, ordering=1, name="Appraisal deadline", complete=False,
                                   agent_email=agent_email, date=today)
                step_thirteen = Step(client=c, ordering=1, name="Loan deadline ", complete=False,
                                     agent_email=agent_email, date=today)
                step_fourteen = Step(client=c, ordering=1, name="Final walkthrough", complete=False,
                                     agent_email=agent_email, date=today)
                step_fifteen = Step(client=c, ordering=1, name="Closing day", complete=False, agent_email=agent_email, date=today)
                step_one.save()
                step_two.save()
                step_three.save()
                step_four.save()
                step_five.save()
                step_six.save()
                step_seven.save()
                step_eight.save()
                step_nine.save()
                step_ten.save()
                step_eleven.save()
                step_twelve.save()
                step_thirteen.save()
                step_fourteen.save()
                step_fifteen.save()
            else:
                print('bye')
                step_one = Step(client=c, ordering=1, name="Set an appointment", complete=False,
                                agent_email=agent_email, date=today)
                step_two = Step(client=c, ordering=1, name="Create CMA report", complete=False, agent_email=agent_email, date=today)
                step_three = Step(client=c, ordering=1, name="Create marketing plan", complete=False,
                                  agent_email=agent_email, date=today)
                step_four = Step(client=c, ordering=1, name="Take notes at client’s house", complete=False,
                                 agent_email=agent_email, date=today)
                step_five = Step(client=c, ordering=1, name="Create updated CMA report", complete=False,
                                 agent_email=agent_email, date=today)
                step_six = Step(client=c, ordering=1, name="Confirm staging", complete=False, agent_email=agent_email, date=today)
                step_seven = Step(client=c, ordering=1, name="Arrange photo shoot", complete=False,
                                  agent_email=agent_email, date=today)
                step_eight = Step(client=c, ordering=1, name="List the property", complete=False,
                                  agent_email=agent_email, date=today)
                step_nine = Step(client=c, ordering=1, name="Open house", complete=False, agent_email=agent_email, date=today)
                step_ten = Step(client=c, ordering=1, name="Offer deadline", complete=False, agent_email=agent_email, date=today)
                step_eleven = Step(client=c, ordering=1, name="Offer accepted", complete=False, agent_email=agent_email, date=today)
                step_twelve = Step(client=c, ordering=1, name="Inspections deadline", complete=False,
                                   agent_email=agent_email, date=today)
                step_thirteen = Step(client=c, ordering=1, name="Reply to inspections deadline ", complete=False,
                                     agent_email=agent_email, date=today)
                step_fourteen = Step(client=c, ordering=1, name="Loan deadline", complete=False,
                                     agent_email=agent_email, date=today)
                step_fifteen = Step(client=c, ordering=1, name="Closing day", complete=False, agent_email=agent_email, date=today)
                step_one.save()
                step_two.save()
                step_three.save()
                step_four.save()
                step_five.save()
                step_six.save()
                step_seven.save()
                step_eight.save()
                step_nine.save()
                step_ten.save()
                step_eleven.save()
                step_twelve.save()
                step_thirteen.save()
                step_fourteen.save()
                step_fifteen.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)

class UpcomingSteps(APIView):

    def get(self, request):
        agent = request.user

        agent_email = agent.email
        today = dt.date.today()
        end_date = today + dt.timedelta(5)
        steps = Step.objects.filter(date__range=[today, end_date]).filter(agent_email=agent_email).filter(complete=False)
        print(steps)

        serializer = StepSerializer(steps, many=True)
        print(serializer.data)

        return Response(serializer.data, status=status.HTTP_200_OK)


class ClientSteps(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = [OAuth2Authentication]

    def post(self, request):
        agent = request.user
        email = request.data.get('email')
        client_type = request.data.get('client_type')

        try:
            clients = agent.client_set.filter(email=email, client_type=client_type)
        except:
            return Response("Not a Client", status=status.HTTP_400_BAD_REQUEST)
        client = clients[0]
        steps = client.step_set.all().order_by('date')

        serializer = StepSerializer(steps, many=True)
        print('hi')
        print(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SingleStep(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = [OAuth2Authentication]

    def post(self, request):
        agent = request.user
        id = request.data.get('id')

        try:
            step = Step.objects.get(id=id)
        except:
            return Response("Not a Step", status=status.HTTP_400_BAD_REQUEST)

        serializer = StepSerializer(step)
        print(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UpdateStep(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = [OAuth2Authentication]

    def post(self, request):
        agent = request.user
        id = request.data.get('id')
        name = request.data.get('name')
        newDate = request.data.get('date')
        date = datetime.strptime(newDate, '%m/%d/%Y')
        complete = request.date.get('complete')

        try:
            step = Step.objects.get(id=id)
        except:
            return Response("Not a Step", status=status.HTTP_400_BAD_REQUEST)

        step.complete = complete
        step.name = name
        step.date = date
        step.save()
        return Response("Updated Step", status=status.HTTP_200_OK)



class RemoveClient(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = [OAuth2Authentication]

    def post(self, request):
        agent = request.user
        email = request.data.get('email')
        client_type = request.data.get('client_type')

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



class UpdateSteps(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = [OAuth2Authentication]

    def post(self, request):
        agent = request.user
        print(agent)
        steps = request.data.get('steps')
        steps_deleted = request.data.get('steps_deleted')
        id = request.data.get('id')
        steps_complete = request.data.get('steps_complete')
        steps_percentage = request.data.get('steps_percentage')
        total_steps = request.data.get('total_steps')


        try:
            client = Client.objects.get(id=id)
        except:
            return Response("Not a Client", status=status.HTTP_400_BAD_REQUEST)
        client.steps_complete = steps_complete
        client.steps_percentage = steps_percentage
        client.total_steps = total_steps
        client.save()
        print(steps_percentage)
        print('steps deleted')
        print(steps_deleted)
        for x in steps_deleted:
            print(x)
            id=x["id"]
            print('id')
            print(id)
            step = Step.objects.get(id=id)
            print('here')
            step.delete()


        for x in steps:
            print('this step')
            print(x)
            id=x["id"]
            complete = x["complete"]
            name = x["name"]
            newdate = x["date"]
            date = datetime.strptime(newdate, '%m/%d/%Y')
            print(name)
            print(newdate)
            print(date)

            step = Step.objects.get(id=id)
            step.complete = complete
            step.name = name
            step.date = date
            step.save()

        return Response("leggo", status=status.HTTP_200_OK)

class AddStep(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = [OAuth2Authentication]

    def post(self, request):
        agent = request.user
        print(agent)
        agent_email = agent.email
        id = request.data.get('id')
        newStepName = request.data.get('newStepName')
        newStepDate = request.data.get('newStepDate')
        total_steps = request.data.get('total_steps')
        steps_percentage = request.data.get('steps_percentage')
        date = datetime.strptime(newStepDate, '%m/%d/%Y')


        try:
            client = Client.objects.get(id=id)
        except:
            return Response("Not a Client", status=status.HTTP_400_BAD_REQUEST)
        client.total_steps = total_steps
        client.steps_percentage = steps_percentage
        client.save()

        try:
            c = Client.objects.get(id=id)
        except:
            return Response("Not a Client", status=status.HTTP_400_BAD_REQUEST)

        step = Step(client=c, ordering=1, name=newStepName, complete=False, agent_email=agent_email, date=date)
        step.save()

        return Response("added", status=status.HTTP_200_OK)





