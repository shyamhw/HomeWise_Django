from django.shortcuts import render

from Agent.models import User
from Agent.models import Agent
from Agent.models import Client
from Agent.models import Step
from Agent.models import Vendor
from Agent.models import VendorRegion
from Agent.models import MLSRegion
from Agent.models import Tag
from Agent.serializers import AgentSerializer
from Agent.serializers import ClientSerializer
from Agent.serializers import StepSerializer
from Agent.serializers import VendorSerializer
from Agent.serializers import VendorRegionSerializer
from Agent.serializers import UserSerializer

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

from django.db.models import Q

## Standard errors
agentDNE = {'code': 0, 'message': 'No agent exists with this email address.'}
agentBadPassword = {'code': 1, 'message': 'Incorrect password.'}
agentTempPassword = {'code': 2, 'message': 'Agent has temporary password. Must change password immediately.'}
clientDNE = {'code': 3, 'message': 'No client exists with this email address.'}
vendorDNE = {'code': 4, 'message': 'No vendor exists with this email address.'}

class AgentsList(APIView):
    serializer_class = AgentSerializer
    permission_classes = (AllowAny,)

    def get(self, request):
        agents = Agent.objects.all()
        serializer = AgentSerializer(agents, many=True)
        return Response(serializer.data)

class AgentUserRegister(APIView):
    """
    Updated
    Register an Agent with an associated User model.
    """
    permission_classes = (AllowAny,)    

    def post(self, request):
        """
        :param first_name
        :param last_name
        :param email
        :param password
        :param mls_region
        :param mls_id
        :param birthday
        """

        # required_fields = ['first_name', 'last_name', 'email', 'password', 'mls_region', 'mls_id']
        #
        # print(request.data.keys())
        # print([elem in request.data.keys() for elem in required_fields])

        # if not all([elem in request.data.keys() for elem in required_fields]):
        #     return Response("Required fields are missing.", status=status.HTTP_400_BAD_REQUEST)

        email = request.data.get('email')
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')
        password = request.data.get('password')
        mls_id = request.data.get('mls_id')
        mls_region = request.data.get('mls_region')
        birthday = request.data.get('birthday')

        birthday_temp = request.data.get('birthday')
        birthday = datetime.strptime(birthday_temp, '%m/%d/%Y')

        print(birthday)
        print(email)
        old_user = User.objects.filter(email=email)
        old_agent = Agent.objects.filter(mls_region=mls_region, mls_id=mls_id)
        if old_user or old_agent:
            return Response("User exists", status=status.HTTP_400_BAD_REQUEST)
        else:
            new_user = User(email=email, first_name=first_name, last_name=last_name)
            new_user.set_password(password)
            new_user.save()
            new_agent = Agent(email=email, mls_id=mls_id, mls_region=mls_region, birthday=birthday, user=new_user)
            new_agent.save()

        ## Create User object
        # new_user = User(
        #         first_name = request.data['first_name'],
        #         last_name = request.data['last_name'],
        #         email = request.data['email']
        #     )
        # new_user.set_password(request.data['password'])
        # new_user.save()
        #
        # ## Create Agent object
        # new_agent = Agent(
        #         mls_id = request.data['mls_id'],
        #         mls_region = request.data['mls_region']
        #     )
        # if 'birthday' in request.data.keys():
        #     new_agent.birthday = request.data['birthday']
        # new_agent.user = new_user
        # new_agent.save()

        return Response("Successfully created agent", status=status.HTTP_201_CREATED)

class ClientUserRegister(APIView):

    serializer_class = AgentSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        email = request.data.get('email')
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')
        password = request.data.get('password')

        old_user = User.objects.filter(email=email)
        if old_user:
            return Response("User exists", status=status.HTTP_400_BAD_REQUEST)
        else:
            new_user = User(email=email, first_name=first_name, last_name=last_name)
            new_user.set_password(password)
            new_user.save()
            clients = Client.objects.filter(email=email)
            for client in clients:
                client.user = new_user
                client.save()

            return Response("Successfully created Client User", status=status.HTTP_201_CREATED)





### DEPRECATED
class AgentRegister(APIView):
    """
    Register a new user.
    """
    serializer_class = AgentSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

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
        user_type = request.data.get('user_type')

        if user_type == 'Client':
            try:
                client = Client.objects.get(email=email)
            except Exception as e:
                return Response(clientDNE, status=status.HTTP_404_NOT_FOUND)
        elif user_type == 'Vendor':
            try:
                vendor = Vendor.objects.get(email=email)
            except Exception as e:
                return Response(vendorDNE, status=status.HTTP_404_NOT_FOUND)
        else:
            try:
                agent = Agent.objects.get(email=email)
            except Exception as e:
                return Response(agentDNE, status=status.HTTP_404_NOT_FOUND)

        try:
            mls_agent = User.objects.get(email=email)
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

        request_email = request.data.get('email')

        try:
            user = User.objects.get(email=request_email)
        except Exception as e:
            return Response("No User found with this email address.", status=status.HTTP_404_NOT_FOUND)

        is_password_correct = user.check_password(request.data.get('current_password'))

        if not is_password_correct:
            return Response("Incorrect password", status=status.HTTP_400_BAD_REQUEST)

        ## Set new password
        request_new_password = request.data.get('new_password')
        result = user.set_new_password(request_new_password)

        if result:
            return Response("Successfully changed password.", status=status.HTTP_200_OK)

        return Response("error", status=status.HTTP_400_BAD_REQUEST)
        

class AgentForgotPassword(APIView):
    """ API to recover password """

    def post(self, request):
        """
        :param email:  email for agent account
        :return success message if reset complete else error message:
        """

        email = request.data.get('email')
        user = User.objects.get(email=email)
        if not user:
            return Response(agentDNE, status=status.HTTP_404_NOT_FOUND)
        # mls_agent = Agent.objects.get(email=email)
        # if not mls_agent:
        #     return Response(agentDNE, status=status.HTTP_404_NOT_FOUND)

        ## Reset password
        result = user.reset_password()

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
            agent_name = agent.user.first_name
            print(agent_name)
            serializer = AgentSerializer(agent)
            print(serializer.data)

            structured_response = {
                'first_name': str(agent.user.first_name),
                'last_name': str(agent.user.last_name),
                'email': str(agent.user.email),
                'mls_region': str(agent.mls_region),
                'mls_id': str(agent.mls_id)
            }

            ##return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(structured_response, status=status.HTTP_200_OK)
        except Agent.DoesNotExist:
            return Response("Not an Agent", status=status.HTTP_400_BAD_REQUEST)

class AgentProfile(APIView):
    serializer_class = AgentSerializer
    permission_classes = (AllowAny,)

    def get(self, request):
        user = request.user
        ##serializer = UserSerializer(user)
        ##agent_serializer = AgentSerializer(user.agent)
        ##return Response(agent_serializer.data)

        structured_response = {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'mls_region': user.agent.mls_region,
            'mls_id': user.agent.mls_id,
            'id': user.id
        }

        return Response(structured_response, status=status.HTTP_200_OK)


class GetClient(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = [OAuth2Authentication]

    def post(self, request):
        user = request.user
        email = request.data.get('email')
        client_type = request.data.get('client_type')

        agent = user.agent

        client = agent.client_set.filter(client_type=client_type).filter(email=email)

        serializer = ClientSerializer(client, many=True)
        print(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ClientGetClient(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = [OAuth2Authentication]

    def post(self, request):
        user = request.user
        email = user.email

        client = user.client
        print(client)
        serializer = ClientSerializer(client)
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

            user = request.user
            agent = user.agent
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


class AddClientNew(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = [OAuth2Authentication]

    def post(self, request):
        user = request.user
        agent_email = request.user.email
        print(user)
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
        vendor_region = request.data.get('vendor_region')
        est_price = int(est_price)
        print('Est price: ' + str(est_price))
        commission = request.data.get('commission')
        commission_val = est_price * (int(commission) / 100)
        print(commission_val)
        if (client_type == 'B'):
            print('bbbb')
            total_steps = 10
        else:
            print('cccc')
            total_steps = 9
        print(total_steps)
        steps_complete = 0
        print(steps_complete)
        steps_percentage = (steps_complete / total_steps) * 100
        print(steps_percentage)
        d = dt.date.today()

        user = request.user
        agent = user.agent
        print(agent)
        client = agent.client_set.filter(email=email, client_type=client_type)
        print(client)
        if client:
            return Response("Already a Client", status=status.HTTP_400_BAD_REQUEST)

        c = Client(email=email, first_name=first_name, last_name=last_name, phone_number=phone_number,
                   client_type=client_type, address=address, city=city, state=state, zipcode=zipcode,
                   est_price=est_price,
                   commission=commission, commission_val=commission_val, total_steps=total_steps,
                   steps_complete=steps_complete, steps_percentage=steps_percentage, vendor_region=vendor_region,
                   agent=agent)
        c.save()

        if (client_type == 'B'):
            print('hi')
            buyers_agreement = request.data.get('buyers_agreement')
            buyers_agreement_format = datetime.strptime(buyers_agreement, '%m/%d/%Y')

            offer_accepted = request.data.get('offer_accepted')
            offer_accepted_format = datetime.strptime(offer_accepted, '%m/%d/%Y')

            est_closing_date = request.data.get('est_closing_date')
            est_closing_date_format = datetime.strptime(est_closing_date, '%m/%d/%Y')

            step_one = Step(client=c, ordering=1, name="Buyer's Agreement", complete=False,
                            agent_email=agent_email, date=buyers_agreement_format)
            step_two = Step(client=c, ordering=2, name="Set up on MLS", complete=False, agent_email=agent_email)
            step_three = Step(client=c, ordering=3, name="Mortgage Pre-Approval", complete=False,agent_email=agent_email)
            step_four = Step(client=c, ordering=4, name="Offer Accepted", complete=False, agent_email=agent_email,
                             date=offer_accepted_format)
            step_five = Step(client=c, ordering=5, name="Deposit", complete=False, agent_email=agent_email)
            step_six = Step(client=c, ordering=6, name="Inspection Deadline", complete=False, agent_email=agent_email)
            step_seven = Step(client=c, ordering=7, name="Appraisal Deadline",complete=False, agent_email=agent_email)
            step_eight = Step(client=c, ordering=8, name="Loan Deadline", complete=False,agent_email=agent_email)
            step_nine = Step(client=c, ordering=9, name="Final Walkthrough", complete=False, agent_email=agent_email)
            step_ten = Step(client=c, ordering=10, name="Estimated Closing Day", complete=False,
                            agent_email=agent_email, date=est_closing_date_format)

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

            return Response("client created", status=status.HTTP_201_CREATED)

        else:
            print('bye')
            listing_date = request.data.get('listing_date')
            listing_date_format = datetime.strptime(listing_date, '%m/%d/%Y')

            offer_accepted = request.data.get('offer_accepted')
            offer_accepted_format = datetime.strptime(offer_accepted, '%m/%d/%Y')

            est_closing_date = request.data.get('est_closing_date')
            est_closing_date_format = datetime.strptime(est_closing_date, '%m/%d/%Y')

            step_one = Step(client=c, ordering=1, name="Staging", complete=False, agent_email=agent_email)
            step_two = Step(client=c, ordering=2, name="Photo Shoot", complete=False, agent_email=agent_email)
            step_three = Step(client=c, ordering=3, name="Listing Date", complete=False,
                              agent_email=agent_email, date=listing_date_format)
            step_four = Step(client=c, ordering=4, name="Open House", complete=False, agent_email=agent_email)
            step_five = Step(client=c, ordering=5, name="Offer Accepted", complete=False,
                             agent_email=agent_email, date=offer_accepted_format)
            step_six = Step(client=c, ordering=6, name="Inspections Deadline", complete=False, agent_email=agent_email)
            step_seven = Step(client=c, ordering=7, name="Reply to Inspections Deadline", complete=False,
                              agent_email=agent_email)
            step_eight = Step(client=c, ordering=8, name="Loan Deadline", complete=False, agent_email=agent_email)
            step_nine = Step(client=c, ordering=9, name="Estimated Closing Day", complete=False, agent_email=agent_email,
                             date=est_closing_date_format)

            step_one.save()
            step_two.save()
            step_three.save()
            step_four.save()
            step_five.save()
            step_six.save()
            step_seven.save()
            step_eight.save()
            step_nine.save()

            return Response("client created", status=status.HTTP_201_CREATED)

        return Response("Client Add Failed", status=status.HTTP_400_BAD_REQUEST)



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
        user = request.user
        print(user)
        agent = user.agent
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

class ClientStepsNew(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = [OAuth2Authentication]

    def post(self, request):
        user = request.user
        print(user)
        agent = user.agent
        email = request.data.get('email')
        client_type = request.data.get('client_type')

        try:
            clients = agent.client_set.filter(email=email, client_type=client_type)
        except:
            return Response("Not a Client", status=status.HTTP_400_BAD_REQUEST)
        client = clients[0]
        steps = client.step_set.all().order_by('ordering', 'date')

        serializer = StepSerializer(steps, many=True)
        print('hi')
        print(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ClientClientSteps(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = [OAuth2Authentication]

    def post(self, request):
        user = request.user
        email = user.email

        client = user.client

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


class DeleteStep(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = [OAuth2Authentication]

    def post(self, request):
        agent = request.user
        client_id = request.data.get('client_id')
        id = request.data.get('id')

        try:
            client = Client.objects.get(id=client_id)
        except:
            return Response("Not a Client", status=status.HTTP_400_BAD_REQUEST)

        try:
            step = Step.objects.get(id=id)
        except:
            return Response("Not a Step", status=status.HTTP_400_BAD_REQUEST)

        if(step.complete):
            new_steps_complete = client.steps_complete - 1
        else:
            new_steps_complete = client.steps_complete

        new_total_steps = client.total_steps - 1
        new_steps_percentage = int(round((new_steps_complete / new_total_steps) * 100))
        client.steps_complete = new_steps_complete
        client.steps_percentage = new_steps_percentage
        client.total_steps = new_total_steps
        client.save()

        step.delete()
        return Response("Step Deleted", status=status.HTTP_200_OK)




class UpdateStep(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = [OAuth2Authentication]

    def post(self, request):
        user = request.user
        print('hi')
        client_id = request.data.get('client_id')
        id = request.data.get('id')
        name = request.data.get('name')
        complete = request.data.get('complete')
        newDate = request.data.get('date')
        print(newDate)
        if newDate is None:
            date = ''
        else:
            date = datetime.strptime(newDate, '%m/%d/%Y')

        print(date)
        try:
            client = Client.objects.get(id=client_id)
        except:
            return Response("Not a Client", status=status.HTTP_400_BAD_REQUEST)

        try:
            step = Step.objects.get(id=id)
        except:
            return Response("Not a Step", status=status.HTTP_400_BAD_REQUEST)

        print(step.complete)
        print(complete)

        if(step.complete != complete):
            print('here')
            #if not currently completed and changing to complete
            if(complete):
                print('a')
                new_steps_complete = client.steps_complete + 1
                new_total_steps = client.total_steps
                new_steps_percentage = int(round((new_steps_complete / new_total_steps) * 100))
                client.steps_complete = new_steps_complete
                client.steps_percentage = new_steps_percentage
            #else if currently true and changing to not complete
            else:
                print('b')
                new_steps_complete = client.steps_complete - 1
                new_total_steps = client.total_steps
                new_steps_percentage = int(round((new_steps_complete / new_total_steps) * 100))
                client.steps_complete = new_steps_complete
                client.steps_percentage = new_steps_percentage

        client.save()

        step.complete = complete
        step.name = name
        if date != '':
            print('here2')
            step.date = date
        step.save()
        return Response("Updated Step", status=status.HTTP_200_OK)



class RemoveClient(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = [OAuth2Authentication]

    def post(self, request):
        user = request.user
        id = request.data.get('id')

        try:
            client = Client.objects.get(id=id)
            client.delete()
            return Response("Client deleted", status=status.HTTP_200_OK)
        except:
            return Response("Not a Client", status=status.HTTP_400_BAD_REQUEST)




class ClientList(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = [OAuth2Authentication]

    def get(self, request):
        user = request.user
        agent = user.agent
        client_type = request.GET.get('client_type')
        clients = {}
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
        agent_email = request.user.email
        id = request.data.get('id')
        newStepName = request.data.get('newStepName')
        newStepDate = request.data.get('newStepDate')
        date = datetime.strptime(newStepDate, '%m/%d/%Y')


        try:
            client = Client.objects.get(id=id)
        except:
            return Response("Not a Client", status=status.HTTP_400_BAD_REQUEST)
        new_total_steps = client.total_steps + 1
        new_steps_complete = client.steps_complete
        new_steps_percentage = int(round((new_steps_complete / new_total_steps) * 100))
        client.total_steps = new_total_steps
        client.steps_percentage = new_steps_percentage
        client.save()

        try:
            c = Client.objects.get(id=id)
        except:
            return Response("Not a Client 2", status=status.HTTP_400_BAD_REQUEST)

        step = Step(client=c, ordering=1, name=newStepName, complete=False, agent_email=agent_email, date=date)
        step.save()

        return Response("added", status=status.HTTP_200_OK)



## Search vendors
class VendorQuery(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = [OAuth2Authentication]

    def get(self, request):
        ## Parse Tags
        query_tags = []
        if 'tags' in request.GET.keys():
            raw_tags = request.GET['tags']
            tag_list = raw_tags.split(",")
            for tag in tag_list:
                clean_tag = tag.strip().replace(" ", "_")
                query_tags.append(clean_tag)

        # if 'tagids' in request.GET.keys():
        #     raw_tagids = request.GET['tags']
        #     tag_list = raw_tagids.split(",")
        #     for tagid in tag_list:
        #         clean_tag_id = int(tag.strip())
        #         clean_tag = Tag(pk=)

        ## Parse Vendor Region
        query_region = None
        if 'region' in request.GET.keys():
            param_region = request.GET['region']
            query_region = VendorRegion(name=param_region)
            print(query_region)


        ## Build QuerySet
        qset = Vendor.objects.all()
        if query_region:
            qset = qset.filter(vendor_region__name=query_region.name)
        if len(query_tags) > 0:
            for tag in query_tags:
                qset = qset.filter(tags__name__contains=tag)
        
        ## Evaluate query
        res = list(qset)

        clientResponse = []

        for r in res:
            val = {
                "id": r.id,
                "name": r.company_name,
                "address": r.address,
                "region": r.vendor_region.name
            }
            clientResponse.append(val)

        return Response(clientResponse)

class VendorStepQuery(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = [OAuth2Authentication]

    def post(self, request):
        user = request.user
        # get vendor_region from response
        vendor_region = request.data.get('vendor_region')


        #get tags from response
        tags = request.data.get('tags')
        print(tags)
        if len(tags) == 0:
            return Response("No Vendors", status=status.HTTP_204_NO_CONTENT)

        vendors = Vendor.objects.all()
        print(vendors)
        vendors = vendors.filter(vendor_region=vendor_region)
        print('filter on vendor region')
        print(vendors)
        
        for tag in tags:
            vendors = vendors.filter(tags=tag)

        print('filter on tags too')
        print(vendors)

        serializer = VendorSerializer(vendors, many=True)
        print(serializer.data)

        # res = list(vendors)
        # print(res)

        # clientResponse = []
        #
        # for r in res:
        #     val = {
        #         "id": r.id,
        #         "name": r.company_name,
        #         "phone_number": r.phone_number,
        #         "email"
        #         "address": r.address,
        #         "region": r.vendor_region.name
        #     }
        #     clientResponse.append(val)

        return Response(serializer.data, status=status.HTTP_200_OK)


# Get VendorRegions for MLS of agent
class GetVendorRegions(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = [OAuth2Authentication]

    def post(self, request):
        user = request.user
        mls_region_name = user.agent.mls_region
        print(mls_region_name)

        mls_regions = MLSRegion.objects.all().filter(name=mls_region_name)
        print(mls_regions[0])

        mls_region = mls_regions[0]

        vendor_regions_all = VendorRegion.objects.all()
        print(vendor_regions_all)
        vendor_regions = vendor_regions_all.filter(mls_region=mls_region)

        serializer = VendorRegionSerializer(vendor_regions, many=True)
        print(serializer.data)

        return Response(serializer.data, status=status.HTTP_200_OK)


class RequestCity(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = [OAuth2Authentication]

    def post(self, request):
        user = request.user
        agent = user.agent

        agent.requested = True
        agent.save()

        return Response("City Requested", status=status.HTTP_200_OK)


