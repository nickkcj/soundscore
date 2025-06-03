from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.hashers import make_password
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

# Imports para o Swagger
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from ..models import User
from ..services.user.supabase_client import authenticate_with_jwt
from ..services.user.add_user import add_user_supabase
from ..services.user.delete_user import delete_user_data_supabase
from .serializers import (
    RegisterSerializer, 
    LoginSerializer, 
    UserProfileSerializer,
    UserUpdateSerializer,
    PasswordChangeSerializer,
    DeleteAccountSerializer
)

# Defina as respostas comuns para reutilizar
success_response = openapi.Response(
    description="Operação bem-sucedida",
    schema=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'success': openapi.Schema(type=openapi.TYPE_BOOLEAN, example=True),
            'message': openapi.Schema(type=openapi.TYPE_STRING),
        }
    )
)

error_response = openapi.Response(
    description="Erro na operação",
    schema=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'error': openapi.Schema(type=openapi.TYPE_STRING, example="Mensagem de erro"),
        }
    )
)

@method_decorator(csrf_exempt, name='dispatch')
class RegisterView(APIView):
    """
    API endpoint para registro de usuários.
    """
    permission_classes = [AllowAny]
    authentication_classes = []
    
    @swagger_auto_schema(
        operation_description="Registra um novo usuário no sistema SoundScore",
        operation_summary="Registrar novo usuário",
        request_body=RegisterSerializer,  # Usando o RegisterSerializer específico
        responses={
            201: openapi.Response(
                description="Usuário registrado com sucesso",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN, example=True),
                        'message': openapi.Schema(type=openapi.TYPE_STRING, example="User registered successfully"),
                        'user': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'username': openapi.Schema(type=openapi.TYPE_STRING, example="johndoe"),
                                'email': openapi.Schema(type=openapi.TYPE_STRING, example="john@example.com"),
                            }
                        )
                    }
                )
            ),
            400: openapi.Response(
                description="Erro de validação ou usuário já existe",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING, example="Username already exists"),
                    }
                )
            ),
            500: error_response
        },
        tags=['Autenticação'],
    )
    def post(self, request):
        """
        Cria um novo usuário após validação dos dados.
        Os dados do usuário são esperados no corpo da requisição.
        """
        serializer = RegisterSerializer(data=request.data)  # Usando o RegisterSerializer
        if serializer.is_valid():
            validated_data = serializer.validated_data
            
            # Verificar se usuário ou email já existem
            if User.objects.filter(username=validated_data['username']).exists():
                return Response(
                    {"error": "Username already exists"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if User.objects.filter(email=validated_data['email']).exists():
                return Response(
                    {"error": "Email already exists"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Criar no Supabase - reutilizando o serviço existente
            response = add_user_supabase(
                validated_data['username'], 
                validated_data['password'], 
                validated_data['email']
            )
            
            if "error" in response:
                return Response(
                    {"error": response["error"]},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Criar localmente
            user = User.objects.create(
                username=validated_data['username'],
                email=validated_data['email'],
                password=make_password(validated_data['password'])
            )
            
            
            return Response({
                "success": True,
                "message": "User registered successfully",
                "user": {
                    "username": user.username,
                    "email": user.email
                },
            }, status=status.HTTP_201_CREATED)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class LoginView(APIView):
    """
    API endpoint para login de usuários.
    """
    permission_classes = [AllowAny]
    authentication_classes = []
    
    @swagger_auto_schema(
        operation_description="Autentica um usuário no sistema SoundScore",
        operation_summary="Login de usuário",
        request_body=LoginSerializer,  # Usando o LoginSerializer específico
        responses={
            200: openapi.Response(
                description="Login realizado com sucesso",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN, example=True),
                        'message': openapi.Schema(type=openapi.TYPE_STRING, example="Login successful"),
                        'user': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'id': openapi.Schema(type=openapi.TYPE_INTEGER, example=1),
                                'username': openapi.Schema(type=openapi.TYPE_STRING, example="johndoe"),
                                'email': openapi.Schema(type=openapi.TYPE_STRING, example="john@example.com"),
                            }
                        )
                    }
                )
            ),
            401: openapi.Response(
                description="Credenciais inválidas",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING, example="Invalid password"),
                    }
                )
            ),
            404: openapi.Response(
                description="Usuário não encontrado",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING, example="User does not exist"),
                    }
                )
            ),
        },
        tags=['Autenticação'],
    )
    def post(self, request):
        """
        Autentica um usuário com base nas credenciais fornecidas.
        """
        serializer = LoginSerializer(data=request.data)  # Usando o LoginSerializer
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        
        try:
            # Reutilizando o serviço existente de integração com Supabase
            client = authenticate_with_jwt()
            response = client.table('soundscore_user') \
                .select('id,username,email') \
                .eq('username', username) \
                .limit(1) \
                .execute()
                
            user_data = response.data[0] if response.data else None
            
            if not user_data:
                return Response(
                    {"error": "User does not exist"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Verificar no banco local
            user = User.objects.filter(username=username).first()
            if not user:
                user = User.objects.create(
                    username=user_data['username'],
                    email=user_data.get('email', ''),
                    password=make_password(password)
                )
            
            # Verificar senha
            if user.check_password(password):
                return Response({
                    "success": True,
                    "message": "Login successful",
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email
                    },
                }, status=status.HTTP_200_OK)
            else:
                return Response(
                    {"error": "Invalid password"},
                    status=status.HTTP_401_UNAUTHORIZED
                )
                
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@method_decorator(csrf_exempt, name='dispatch')
class UserProfileView(APIView):
    """
    API endpoint para gerenciar perfis de usuários.
    """
    permission_classes = [AllowAny]
    authentication_classes = []
    
    @swagger_auto_schema(
        operation_description="Retorna o perfil de um usuário específico",
        operation_summary="Obter perfil de usuário",
        manual_parameters=[
            openapi.Parameter(
                'username', 
                openapi.IN_PATH, 
                description="Nome de usuário", 
                type=openapi.TYPE_STRING,
                required=True,
                example="johndoe"
            )
        ],
        responses={
            200: openapi.Response(
                description="Perfil do usuário",
                schema=UserProfileSerializer  # Usando o UserProfileSerializer como schema de resposta
            ),
            404: openapi.Response(
                description="Usuário não encontrado",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING, example="User not found"),
                    }
                )
            ),
        },
        tags=['Perfil de Usuário'],
    )
    def get(self, request, username):
        """
        Retorna as informações do perfil do usuário especificado.
        """
        try:
            user = User.objects.get(username=username)
            
            # Buscar informações adicionais do Supabase
            client = authenticate_with_jwt()
            response = client.table('soundscore_user') \
                .select('id,profile_picture') \
                .eq('username', username) \
                .limit(1) \
                .execute()
                
            profile_data = response.data[0] if response.data else {}
            
            # Adiciona os dados do Supabase ao objeto do usuário
            user.supabase_data = profile_data
            
            # Serializa o perfil do usuário
            serializer = UserProfileSerializer(user, context={'request': request})
            return Response(serializer.data)
            
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @swagger_auto_schema(
        operation_description="Atualiza dados do perfil do usuário",
        operation_summary="Atualizar perfil de usuário",
        manual_parameters=[
            openapi.Parameter(
                'username', 
                openapi.IN_PATH, 
                description="Nome de usuário", 
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        request_body=UserUpdateSerializer,  # Usando o serializer específico para atualização
        responses={
            200: openapi.Response(
                description="Perfil atualizado com sucesso",
                schema=UserProfileSerializer
            ),
            400: error_response,
            404: openapi.Response(
                description="Usuário não encontrado",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING, example="User not found"),
                    }
                )
            ),
        },
        tags=['Perfil de Usuário'],
    )
    def put(self, request, username):
        """
        Atualiza os dados do perfil do usuário.
        """
        try:
            user = User.objects.get(username=username)
            
            serializer = UserUpdateSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                
                # Atualizar no Supabase também
                # ...
                
                return Response({"success": True, "message": "Profile updated successfully"})
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)


@method_decorator(csrf_exempt, name='dispatch')
class DeleteUserView(APIView):
    """
    API endpoint para excluir usuários.
    """
    permission_classes = [AllowAny]
    authentication_classes = []
    
    @swagger_auto_schema(
        operation_description="Exclui um usuário do sistema SoundScore",
        operation_summary="Excluir usuário",
        manual_parameters=[
            openapi.Parameter(
                'username', 
                openapi.IN_PATH, 
                description="Nome de usuário a ser excluído", 
                type=openapi.TYPE_STRING,
                required=True,
                example="johndoe"
            )
        ],
        request_body=DeleteAccountSerializer,  # Usando o serializer específico para exclusão
        responses={
            200: openapi.Response(
                description="Usuário excluído com sucesso",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN, example=True),
                        'message': openapi.Schema(type=openapi.TYPE_STRING, example="User deleted successfully"),
                    }
                )
            ),
            400: openapi.Response(
                description="Dados inválidos",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING, example="Password is required to delete account"),
                    }
                )
            ),
            401: openapi.Response(
                description="Senha inválida",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING, example="Invalid password"),
                    }
                )
            ),
            404: openapi.Response(
                description="Usuário não encontrado",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING, example="User not found"),
                    }
                )
            ),
        },
        tags=['Perfil de Usuário'],
    )
    def delete(self, request, username):
        """
        Exclui um usuário do banco de dados local e do Supabase.
        Requer senha para confirmar a exclusão.
        """
        serializer = DeleteAccountSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        password = serializer.validated_data['password']

        try:
            # Verificar se o usuário existe
            user = User.objects.filter(username=username).first()
            if not user:
                return Response(
                    {"error": "User not found"},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Verificar senha para confirmar
            if not user.check_password(password):
                return Response(
                    {"error": "Invalid password"},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            # Excluir do Supabase
            delete_result = delete_user_data_supabase(username)
                
            if "error" in delete_result:
                return Response(
                    {"error": delete_result["error"]},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Excluir do Django
            user.delete()

            return Response(
                {"success": True, "message": "User deleted successfully"},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )