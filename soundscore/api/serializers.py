from rest_framework import serializers
from ..models import User
from ..validation.pydantic_schemas import RegisterSchema
from pydantic import ValidationError as PydanticValidationError

class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer para registro de novos usuários.
    Utiliza validação Pydantic existente para garantir consistência.
    """
    username = serializers.CharField(
        help_text="Nome de usuário único para identificação no sistema",
        min_length=3,
        max_length=100
    )
    email = serializers.EmailField(
        help_text="Email válido do usuário para comunicações"
    )
    password = serializers.CharField(
        write_only=True, 
        style={'input_type': 'password'},
        help_text="Senha forte (mínimo 8 caracteres com letras e números)"
    )
    confirm_password = serializers.CharField(
        write_only=True, 
        style={'input_type': 'password'},
        help_text="Confirmação da senha (deve ser idêntica)"
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'confirm_password']

    def validate(self, data):
        """
        Usa o mesmo schema Pydantic para validação consistente em toda a aplicação
        """
        try:
            # Passa os dados para o Pydantic validar
            validated = RegisterSchema(
                username=data.get('username', ''),
                email=data.get('email', ''),
                password=data.get('password', ''),
                confirm_password=data.get('confirm_password', '')
            )
            
            return {
                'username': validated.username,
                'email': validated.email,
                'password': validated.password,
                'confirm_password': validated.confirm_password
            }
            
        except PydanticValidationError as e:
            # Converte erros do Pydantic para o formato do DRF
            errors = {}
            for error in e.errors():
                field = error['loc'][0]
                message = error['msg']
                # Remove "Value error, " prefixo se presente
                if message.lower().startswith("value error, "):
                    message = message[13:]
                
                if field in errors:
                    errors[field].append(message)
                else:
                    errors[field] = [message]
            
            raise serializers.ValidationError(errors)


class LoginSerializer(serializers.Serializer):
    """
    Serializer para autenticação de usuários existentes.
    """
    username = serializers.CharField(
        required=True,
        help_text="Nome de usuário cadastrado"
    )
    password = serializers.CharField(
        required=True, 
        style={'input_type': 'password'},
        help_text="Senha do usuário",
        write_only=True
    )


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer para visualização de perfis de usuário.
    """
    profile_picture = serializers.CharField(
        required=False, 
        allow_null=True,
        help_text="URL da imagem de perfil do usuário"
    )
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'created_at', 'profile_picture']
        read_only_fields = ['id', 'created_at']
        
    def to_representation(self, instance):
        """
        Adiciona dados do Supabase se disponíveis
        """
        data = super().to_representation(instance)
        request = self.context.get('request')
        
        # O campo profile_picture não vem do modelo User, é adicionado aqui
        if hasattr(instance, 'supabase_data') and instance.supabase_data:
            data['profile_picture'] = instance.supabase_data.get('profile_picture')
            
        return data


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer para atualização de dados de perfil.
    """
    email = serializers.EmailField(
        required=False,
        help_text="Novo email do usuário"
    )
    profile_picture = serializers.CharField(
        required=False,
        allow_null=True,
        allow_blank=True,
        help_text="URL da imagem de perfil"
    )
    bio = serializers.CharField(
        required=False, 
        allow_blank=True,
        help_text="Biografia do usuário"
    )
    
    class Meta:
        model = User
        fields = ['email', 'profile_picture', 'bio']


class PasswordChangeSerializer(serializers.Serializer):
    """
    Serializer para alteração de senha.
    """
    current_password = serializers.CharField(
        required=True,
        style={'input_type': 'password'},
        help_text="Senha atual para verificação",
        write_only=True
    )
    new_password = serializers.CharField(
        required=True,
        style={'input_type': 'password'},
        help_text="Nova senha (mínimo 8 caracteres com letras e números)",
        write_only=True
    )
    confirm_new_password = serializers.CharField(
        required=True,
        style={'input_type': 'password'},
        help_text="Confirmação da nova senha",
        write_only=True
    )
    
    def validate(self, data):
        """
        Verifica se as senhas novas coincidem.
        """
        if data['new_password'] != data['confirm_new_password']:
            raise serializers.ValidationError({"confirm_new_password": "As senhas não coincidem"})
        return data


class DeleteAccountSerializer(serializers.Serializer):
    """
    Serializer para confirmar a exclusão de conta.
    """
    password = serializers.CharField(
        required=True,
        style={'input_type': 'password'},
        help_text="Senha do usuário para confirmar exclusão",
        write_only=True
    )
    confirmation = serializers.BooleanField(
        required=True,
        help_text="Confirmação explícita de que deseja excluir a conta (deve ser true)",
    )
    
    def validate_confirmation(self, value):
        """
        Garante que o usuário confirmou explicitamente a exclusão.
        """
        if not value:
            raise serializers.ValidationError(
                "Você deve confirmar explicitamente a exclusão da conta definindo confirmation=true"
            )
        return value


# Mantendo o UserSerializer original para compatibilidade
class UserSerializer(RegisterSerializer):
    """
    Serializer original para compatibilidade com código existente.
    Recomendado usar os serializers específicos acima para novos endpoints.
    """
    pass