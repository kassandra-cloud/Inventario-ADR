"""
forms.py - Archivo de formularios de la aplicación
Contiene todos los formularios necesarios para manejar los diferentes modelos y funcionalidades
"""

from django import forms
from django.contrib.auth.models import User
from accounts.models import Profile
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import (
    AllInOne, AllInOneAdmins, Notebook, MiniPC,
    Proyectores, BodegaADR, Azotea, Monitor, Audio, Tablet # Nuevos modelos
)
from .opciones import (
    opciones_sala_All_In_One, 
    opciones_estado, 
    opciones_marca_all_in_one,
    opciones_ubicacion_all_in_one_admin,
    opciones_marca_notebook,  # Añadimos esta importación
    opciones_ubicacion_notebook,
    opciones_marca_mini_pc,  # Asegúrate de que exista en opciones.py
    opciones_ubicacion_mini_pc,
    opciones_marca_proyector,
    opciones_activos,
    opciones_marca_azotea,
    opciones_ubicacion_proyector,
    opciones_estado_activo,
    opciones_edificio,
    opciones_marca_monitor, opciones_ubicacion_monitor # Opciones para Monitor
) # Eliminado opciones_ubicacion_tablet y opciones_marca_tablet

# -------- FORMULARIOS DE AUTENTICACIÓN --------

class LoginForm(AuthenticationForm):
    """Formulario de inicio de sesión"""
    pass

class RegisterUserForm(forms.ModelForm):
    """Formulario para registro de nuevos usuarios"""
    # Campos adicionales requeridos
    first_name = forms.CharField(label='Nombres', required=True)
    last_name = forms.CharField(label='Apellidos', required=True)
    password1 = forms.CharField(
        label='Contraseña', 
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña'}),
        required=True
    )
    password2 = forms.CharField(
        label='Confirmar Contraseña', 
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirmar Contraseña'}),
        required=True
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Nombre de Usuario'}),
            'first_name': forms.TextInput(attrs={'placeholder': 'Nombre'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Apellidos'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Correo Electrónico'}),
        }

    def clean_email(self):
        """Validación personalizada para email único"""
        email_field = self.cleaned_data.get('email')
        if User.objects.filter(email=email_field).exists():
            raise forms.ValidationError('Este email ya existe en los registros')
        return email_field

    def clean(self):
        """Validación personalizada para verificar que las contraseñas coincidan"""
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            self.add_error("password2", "Las contraseñas no coinciden")

        # Validación de fortaleza de contraseña (opcional)
        if password1:
            if len(password1) < 8:
                self.add_error("password1", "La contraseña debe tener al menos 8 caracteres")
            if not any(char.isdigit() for char in password1):
                self.add_error("password1", "La contraseña debe contener al menos un número")
            if not any(char.isalpha() for char in password1):
                self.add_error("password1", "La contraseña debe contener al menos una letra")

        return cleaned_data

class UserForm(forms.ModelForm):
    """Formulario para actualización de datos básicos del usuario"""
    class Meta:
        model = User
        fields = ['first_name', 'last_name']

class ProfileForm(forms.ModelForm):
    """Formulario para el perfil de usuario"""
    class Meta:
        model = Profile
        fields = ['image']

# -------- FORMULARIOS DE EQUIPOS --------

class AllInOneForm(forms.ModelForm):
    """
    Formulario para All In One
    Incluye campo activo predeterminado y no editable
    """
    # Campo activo configurado como readonly con valor predeterminado
    activo = forms.CharField(
        initial='All in One',  # Valor predeterminado
        max_length=150,
        required=True,
        widget=forms.TextInput(
            attrs={
                'readonly': 'readonly',
                'class': 'w-full rounded-md border-gray-300 shadow-sm bg-gray-100 cursor-not-allowed'
            }
        )
    )
    
    class Meta:
        model = AllInOne
        fields = ['activo', 'estado', 'marca', 'modelo', 'n_serie', 'unive', 'bdo', 'netbios', 'ubicacion']
        widgets = {
            'estado': forms.Select(choices=opciones_estado),
            'marca': forms.TextInput(attrs={
                'class': 'w-full rounded-md shadow-sm border-gray-300', # Clases de Tailwind para input
                'list': 'marcas_list', # Apunta al ID del datalist
                'placeholder': 'Seleccione o escriba una marca'
            }),
            'ubicacion': forms.TextInput(attrs={
                'class': 'w-full rounded-md border-gray-300 shadow-sm',
                'placeholder': 'Ingrese la ubicación'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Establecer el valor inicial para 'marca' si estamos editando
        if self.instance and self.instance.pk:
            self.initial['marca'] = self.instance.marca

    def clean_marca(self):
        marca = self.cleaned_data.get('marca')
        if not marca:
            raise forms.ValidationError('Este campo es obligatorio.')
        # Aquí podrías añadir lógica para capitalizar la marca o limpiarla si es necesario.
        # Por ejemplo: marca = marca.strip().capitalize()
        return marca.strip()


    def clean_n_serie(self):
        """Validación para número de serie único"""
        n_serie = self.cleaned_data.get('n_serie')
        print(f"Validando n_serie: {n_serie}, Instance ID: {self.instance.id}")
        if AllInOne.objects.exclude(id=self.instance.id).filter(n_serie=n_serie).exists():
            raise forms.ValidationError('Este Número de Serie ya existe')
        return n_serie

    def clean_modelo(self):
        """Validación para campo modelo obligatorio"""
        modelo = self.cleaned_data.get('modelo')
        if not modelo:
            raise forms.ValidationError('Este campo es obligatorio')
        return modelo

    def clean_activo(self):
        """
        Asegura que el valor del campo activo siempre sea 'All in One'
        incluso si alguien intenta modificarlo
        """
        return 'All in One'

class AllInOneAdminsForm(forms.ModelForm):
    """
    Formulario para All In One Administrativos
    Incluye campo activo predeterminado y no editable
    """
    # Campo activo configurado como readonly con valor predeterminado
    activo = forms.CharField(
        initial='All in One',  # Valor predeterminado
        max_length=150,
        required=True,
        widget=forms.TextInput(
            attrs={
                'readonly': 'readonly',
                'class': 'w-full rounded-md border-gray-300 shadow-sm bg-gray-100 cursor-not-allowed'
            }
        )
    )

    # Definir explícitamente el campo bdo para asegurar que no sea requerido
    bdo = forms.DecimalField(
        max_digits=30,
        decimal_places=0,
        label='BDO',
        required=False, # Permitir que el campo esté vacío o sea 0
        widget=forms.NumberInput(
            attrs={
                'class': 'w-full rounded-md border-gray-300 shadow-sm',
                'placeholder': 'BDO'
            }
        )
    )
    
    class Meta:
        model = AllInOneAdmins
        fields = ['activo', 'estado', 'marca', 'modelo', 'n_serie', 'unive', 'bdo', 'netbios', 'ubicacion']
        widgets = {
            'estado': forms.Select(choices=opciones_estado),
            'marca': forms.TextInput(attrs={
                'class': 'w-full rounded-md shadow-sm border-gray-300',
                'placeholder': 'Escriba la marca'
            }),
            'ubicacion': forms.TextInput(attrs={
                'class': 'w-full rounded-md border-gray-300 shadow-sm',
                'placeholder': 'Ingrese la ubicación'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Establecer el valor inicial para 'marca' si estamos editando
        if self.instance and self.instance.pk:
            self.initial['marca'] = self.instance.marca
        # Establecer el valor inicial para 'bdo' si estamos editando
        if self.instance and self.instance.pk:
             self.initial['bdo'] = self.instance.bdo


    def clean_marca(self):
        marca = self.cleaned_data.get('marca')
        if not marca:
            raise forms.ValidationError('Este campo es obligatorio.')
        return marca.strip()

    def clean_n_serie(self):
        """Validación para número de serie único"""
        n_serie = self.cleaned_data.get('n_serie')
        if AllInOneAdmins.objects.exclude(id=self.instance.id).filter(n_serie=n_serie).exists():
            raise forms.ValidationError('Este Número de Serie ya existe')
        return n_serie

    def clean_modelo(self):
        """Validación para campo modelo obligatorio"""
        modelo = self.cleaned_data.get('modelo')
        if not modelo:
            raise forms.ValidationError('Este campo es obligatorio')
        return modelo

    def clean_activo(self):
        """
        Asegura que el valor del campo activo siempre sea 'All in One'
        incluso si alguien intenta modificarlo
        """
        return 'All in One'

class NotebooksForm(forms.ModelForm):
    """
    Formulario para Notebooks
    Incluye campo activo predeterminado y no editable
    """
    # Campo activo configurado como readonly con valor predeterminado
    activo = forms.CharField(
        initial='Notebook Avanzado',
        max_length=150,
        required=True,
        widget=forms.TextInput(
            attrs={
                'readonly': 'readonly',
                'class': 'w-full rounded-md border-gray-300 shadow-sm bg-gray-100 cursor-not-allowed'
            }
        )
    )
    
    class Meta:
        model = Notebook
        fields = ['activo', 'asignado_a', 'estado', 'marca', 'modelo', 'n_serie', 'unive', 'bdo', 'netbios', 'ubicacion']
        widgets = {
            'estado': forms.Select(choices=opciones_estado),
            'marca': forms.TextInput(attrs={
                'class': 'w-full rounded-md shadow-sm border-gray-300',
                'list': 'marcas_list_notebook', # ID único para el datalist de notebook
                'placeholder': 'Seleccione o escriba una marca'
            }),
            'ubicacion': forms.TextInput(attrs={
                'class': 'w-full rounded-md border-gray-300 shadow-sm',
                'placeholder': 'Ingrese la ubicación'
            }),
             'bdo': forms.NumberInput(attrs={ # Definir explícitamente el widget para BDO
                'class': 'w-full rounded-md border-gray-300 shadow-sm',
                'placeholder': 'BDO'
            }),
        }

    bdo = forms.DecimalField( # Definir explícitamente el campo BDO
        max_digits=30,
        decimal_places=0,
        label='BDO',
        required=False, # Establecer como no requerido
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Establecer el valor inicial para 'marca' si estamos editando
        if self.instance and self.instance.pk:
            self.initial['marca'] = self.instance.marca
        # Establecer el valor inicial para 'bdo' si estamos editando
        if self.instance and self.instance.pk:
             self.initial['bdo'] = self.instance.bdo


    def clean_marca(self):
        marca = self.cleaned_data.get('marca')
        if not marca:
            raise forms.ValidationError('Este campo es obligatorio.')
        return marca.strip()

    def clean_n_serie(self):
        """Validación para número de serie único"""
        n_serie = self.cleaned_data.get('n_serie')
        if Notebook.objects.exclude(id=self.instance.id).filter(n_serie=n_serie).exists():
            raise forms.ValidationError('Este Número de Serie ya existe')
        return n_serie

    def clean_modelo(self):
        """Validación para campo modelo obligatorio"""
        modelo = self.cleaned_data.get('modelo')
        if not modelo:
            raise forms.ValidationError('Este campo es obligatorio')
        return modelo

    def clean_activo(self):
        """
        Asegura que el valor del campo activo siempre sea 'Notebook Avanzado'
        incluso si alguien intenta modificarlo
        """
        return 'Notebook Avanzado'

class MiniPCForm(forms.ModelForm):
    """
    Formulario para Mini PC
    Incluye campo activo predeterminado y no editable
    """
    # Campo activo configurado como readonly con valor predeterminado
    activo = forms.CharField(
        initial='Mini PC',
        max_length=150,
        required=True,
        widget=forms.TextInput(
            attrs={
                'readonly': 'readonly',
                'class': 'w-full rounded-md border-gray-300 shadow-sm bg-gray-100 cursor-not-allowed'
            }
        )
    )
    
    class Meta:
        model = MiniPC
        fields = ['activo', 'estado', 'marca', 'modelo', 'n_serie', 'unive', 'bdo', 'ubicacion']
        widgets = {
            'estado': forms.TextInput(attrs={
                'class': 'w-full rounded-md border-gray-300 shadow-sm',
                'placeholder': 'Ingrese el estado'
            }),
            'marca': forms.TextInput(attrs={
                'class': 'w-full rounded-md shadow-sm border-gray-300',
                'list': 'marcas_list_minipc',
                'placeholder': 'Seleccione o escriba una marca'
                }),
                'ubicacion': forms.TextInput(attrs={
                    'class': 'w-full rounded-md border-gray-300 shadow-sm',
                    'placeholder': 'Ingrese la ubicación'
                })
            }
            
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            # Establecer el valor inicial para 'marca' si estamos editando
            if self.instance and self.instance.pk:
                self.initial['marca'] = self.instance.marca

    def clean_marca(self):
        marca = self.cleaned_data.get('marca')
        if not marca:
            raise forms.ValidationError('Este campo es obligatorio.')
        return marca.strip()

    def clean_n_serie(self):
        """Validación para número de serie único"""
        n_serie = self.cleaned_data.get('n_serie')
        if MiniPC.objects.exclude(id=self.instance.id).filter(n_serie=n_serie).exists():
            raise forms.ValidationError('Este Número de Serie ya existe')
        return n_serie

    def clean_modelo(self):
        """Validación para campo modelo obligatorio"""
        modelo = self.cleaned_data.get('modelo')
        if not modelo:
            raise forms.ValidationError('Este campo es obligatorio')
        return modelo

    def clean_activo(self):
        """
        Asegura que el valor del campo activo siempre sea 'Mini PC'
        incluso si alguien intenta modificarlo
        """
        return 'Mini PC'

class ProyectoresForm(forms.ModelForm):
    """
    Formulario para Proyectores.
    Incluye campo activo predeterminado y no editable.
    """
    # Campo activo configurado como readonly con valor predeterminado
    activo = forms.CharField(
        initial='Proyector',  # Valor predeterminado
        max_length=150,
        required=True,
        widget=forms.TextInput(
            attrs={
                'readonly': 'readonly',
                'class': 'w-full rounded-md border-gray-300 shadow-sm bg-gray-100 cursor-not-allowed'
            }
        )
    )

    class Meta:
        model = Proyectores
        fields = ['activo', 'estado', 'marca', 'modelo', 'n_serie', 'ubicacion']
        widgets = {
            'estado': forms.Select(choices=opciones_estado),
            'marca': forms.TextInput(attrs={
                'class': 'w-full rounded-md shadow-sm border-gray-300',
                'list': 'marcas_list_proyector',
                'placeholder': 'Seleccione o escriba una marca'
            }),
            'ubicacion': forms.TextInput(attrs={'class': 'w-full rounded-md shadow-sm border-gray-300'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Establecer el valor inicial para 'marca' si estamos editando
        if self.instance and self.instance.pk:
            self.initial['marca'] = self.instance.marca

    def clean_marca(self):
        marca = self.cleaned_data.get('marca')
        if not marca:
            raise forms.ValidationError('Este campo es obligatorio.')
        return marca.strip()

    def clean_n_serie(self):
        """Validación para número de serie único"""
        n_serie = self.cleaned_data.get('n_serie')
        if Proyectores.objects.exclude(id=self.instance.id).filter(n_serie=n_serie).exists():
            raise forms.ValidationError('Este Número de Serie ya existe')
        return n_serie

    def clean_modelo(self):
        """Validación para campo modelo obligatorio"""
        modelo = self.cleaned_data.get('modelo')
        if not modelo:
            raise forms.ValidationError('El campo "Modelo" es obligatorio.')
        return modelo

    def clean_activo(self):
        """
        Asegura que el valor del campo activo siempre sea 'Proyector',
        incluso si alguien intenta modificarlo.
        """
        return 'Proyector'






class BodegaADRForm(forms.ModelForm):
    """
    Formulario para Bodega ADR
    - Mantiene consistencia con campos heredados de EquipoInformatico
    - Incluye validaciones específicas para Bodega
    """
    activo = forms.CharField(
    label="Tipo de Activo",
    max_length=150,
    required=True,
    widget=forms.TextInput(
        attrs={
            'class': 'w-full rounded-md border-gray-300 shadow-sm',
            'placeholder': 'Tipo de Activo'
        }
    )
)
    class Meta:
        model = BodegaADR
        fields = ['activo', 'ubicacion', 'marca', 'modelo', 'n_serie', 'unive', 'bdo', 'netbios'] # Renombrado estado_activo a ubicacion
        widgets = {
            'ubicacion': forms.TextInput( # Renombrado estado_activo a ubicacion y cambiado a TextInput
                attrs={
                    'class': 'w-full rounded-md border-gray-300 shadow-sm',
                    'placeholder': 'Ingrese la ubicación'
                }
            ),
            'marca': forms.TextInput(
                attrs={
                    'class': 'w-full rounded-md shadow-sm border-gray-300',
                    'placeholder': 'Escriba la marca' # Placeholder actualizado
                }
            ),
            'modelo': forms.TextInput(
                attrs={
                    'class': 'w-full rounded-md border-gray-300 shadow-sm',
                    'placeholder': 'Modelo'
                }
            ),
            'n_serie': forms.TextInput(
                attrs={
                    'class': 'w-full rounded-md border-gray-300 shadow-sm',
                    'placeholder': 'Número de Serie'
                }
            ),
            'unive': forms.TextInput(
                attrs={
                    'class': 'w-full rounded-md border-gray-300 shadow-sm',
                    'placeholder': 'UNIVE'
                }
            ),
            'bdo': forms.NumberInput(
                attrs={
                    'class': 'w-full rounded-md border-gray-300 shadow-sm',
                    'placeholder': 'BDO',
                    'required': True  # Marcamos el campo como requerido
                }
            ),
            'netbios': forms.TextInput(
                attrs={
                    'class': 'w-full rounded-md border-gray-300 shadow-sm',
                    'placeholder': 'NetBios'
                }
            )
        }
        
            
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ya no se asignan 'choices' al widget de marca
        
        # Establecer el valor inicial para 'marca' si estamos editando
        if self.instance and self.instance.pk:
            self.initial['marca'] = self.instance.marca

        # El bloque anterior para manejar choices dinámicas de ubicación ya no es necesario
        # porque 'ubicacion' es ahora un TextInput.




    def clean_n_serie(self):
        """Validación para número de serie único"""
        n_serie = self.cleaned_data.get('n_serie')
        if BodegaADR.objects.exclude(id=self.instance.id).filter(n_serie=n_serie).exists():
            raise forms.ValidationError('Este Número de Serie ya existe')
        return n_serie

    def clean_modelo(self):
        """Validación para campo modelo obligatorio"""
        modelo = self.cleaned_data.get('modelo')
        if not modelo:
            raise forms.ValidationError('Este campo es obligatorio')
        return modelo

    def clean_activo(self):
        """Validación para asegurar selección de activo"""
        activo = self.cleaned_data.get('activo')
        if not activo or activo == '':
            raise forms.ValidationError('Debe seleccionar un tipo de activo')
        return activo

    def clean_ubicacion(self):
        ubicacion = self.cleaned_data.get('ubicacion')
        if not ubicacion: # Asegurarse que la ubicación no esté vacía
            raise forms.ValidationError('Este campo es obligatorio.')
        return ubicacion.strip() # Simplemente limpiar espacios en blanco

    def clean_marca(self):
        """Validación para asegurar que el campo marca no esté vacío."""
        marca = self.cleaned_data.get('marca')
        if not marca: # Verifica si el campo está vacío
            raise forms.ValidationError('Este campo es obligatorio.')
        return marca.strip() # Limpiar espacios en blanco

    # def clean_bdo(self):
    #     """Validación obligatoria y de formato para BDO"""
    #     bdo = self.cleaned_data.get('bdo')
    #     if not bdo:
    #         raise forms.ValidationError('El campo BDO es requerido')
        
    #     try:
    #         # Asegurarse que sea un número entero válido y no esté vacío
    #         bdo_str = str(bdo).strip()  # Eliminar espacios en blanco
    #         if not bdo_str:
    #             raise forms.ValidationError('El campo BDO es requerido')
                
    #         bdo_int = int(bdo_str)
    #         if bdo_int <= 0:
    #             raise forms.ValidationError('El BDO debe ser un número positivo')
    #         return bdo_int  # Retornar el valor como entero
    #     except (ValueError, TypeError):
    #         raise forms.ValidationError('El campo BDO solo debe contener números')

    def clean(self):
        """
        Validación general del formulario
        Asegura consistencia entre campos relacionados
        """
        cleaned_data = super().clean()
        
        # Validación de campos obligatorios
        required_fields = {
            'activo': 'El tipo de activo es requerido',
            'ubicacion': 'La ubicación es requerida',
            'marca': 'La marca es requerida',
            'modelo': 'El modelo es requerido',
            'n_serie': 'El número de serie es requerido'
        }

        for field, error in required_fields.items():
            if not cleaned_data.get(field):
                self.add_error(field, error)

        # Validación específica para selecciones en dropdowns
        dropdowns = {
            'activo': 'Debe seleccionar un tipo de activo',
            'marca': 'Debe seleccionar una marca',
            'ubicacion': 'Debe seleccionar una ubicación'
        }

        for field, error in dropdowns.items():
            value = cleaned_data.get(field)
            if value == '':
                self.add_error(field, error)

        return cleaned_data

class AzoteaForm(forms.ModelForm):
    """
    Formulario para Azotea
    Permite texto libre para Activo y Ubicación.
    """
    activo = forms.CharField( # Cambiado a CharField para permitir texto libre
        label="Tipo de Activo",
        max_length=150, # Añadir max_length para CharField
        required=True,
        widget=forms.TextInput( # Usar TextInput para entrada de texto
            attrs={
                'class': 'w-full rounded-md border-gray-300 shadow-sm' # Clases de Tailwind para input
            }
        )
    )

    class Meta:
        model = Azotea
        fields = ['activo', 'estado', 'ubicacion', 'marca', 'modelo', 'n_serie', 'unive', 'bdo']
        widgets = {
            'ubicacion': forms.TextInput(
                attrs={
                    'class': 'w-full rounded-md border-gray-300 shadow-sm',
                    'placeholder': 'Ingrese la ubicación'
                }
            ),
            'marca': forms.TextInput(
                attrs={
                    'class': 'w-full rounded-md shadow-sm border-gray-300',
                    'list': 'marcas_azotea_list', # Apunta al ID del datalist
                    'placeholder': 'Seleccione o escriba una marca'
                }
            ),
            'modelo': forms.TextInput(
                attrs={
                    'class': 'w-full rounded-md border-gray-300 shadow-sm',
                    'placeholder': 'Modelo'
                }
            ),
            'n_serie': forms.TextInput(
                attrs={
                    'class': 'w-full rounded-md border-gray-300 shadow-sm',
                    'placeholder': 'Número de Serie'
                }
            ),
             'unive': forms.TextInput(
                attrs={
                    'class': 'w-full rounded-md border-gray-300 shadow-sm',
                    'placeholder': 'UNIVE'
                }
            ),
             'bdo': forms.NumberInput(
                attrs={
                    'class': 'w-full rounded-md border-gray-300 shadow-sm',
                    'placeholder': 'BDO',
                    'required': True
                }
            )
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Pasar las opciones de marca al widget para el datalist
        self.fields['marca'].widget.attrs['choices'] = opciones_marca_azotea

        # Establecer el valor inicial para 'marca' si estamos editando
        if self.instance and self.instance.pk:
            self.initial['marca'] = self.instance.marca



    def clean_n_serie(self):
        """Validación para número de serie único"""
        n_serie = self.cleaned_data.get('n_serie')
        if Azotea.objects.exclude(id=self.instance.id).filter(n_serie=n_serie).exists():
            raise forms.ValidationError('Este Número de Serie ya existe')
        return n_serie


    def clean(self):
        """
        Validación general del formulario
        Asegura consistencia entre campos relacionados
        """
        cleaned_data = super().clean()
        
        # Validación de campos obligatorios
        required_fields = {
            'activo': 'El tipo de activo es requerido',
            'marca': 'La marca es requerida',
            'modelo': 'El modelo es requerido',
            'n_serie': 'El número de serie es requerido',
            # 'bdo': 'El BDO es requerido'
        }

        for field, error in required_fields.items():
            if not cleaned_data.get(field):
                self.add_error(field, error)

        # Validación específica para selecciones en dropdowns
        # Eliminada ya que los campos ahora permiten texto libre.
        # dropdowns = {
        #     'activo': 'Debe seleccionar un tipo de activo',
        #     'marca': 'Debe seleccionar una marca', # Esta validación podría necesitar ajuste si marca también se vuelve texto libre
        #     'ubicacion': 'Debe ingresar una ubicación'
        # }

        # for field, error in dropdowns.items():
        #     value = cleaned_data.get(field)
        #     if value == '':
        #         self.add_error(field, error)

        return cleaned_data

# -------- FORMULARIOS DE NUEVOS ACTIVOS --------

class MonitorForm(forms.ModelForm):
    """
    Formulario para Monitores
    Incluye campo activo predeterminado y no editable
    """
    activo = forms.CharField(
        initial='Monitor',
        max_length=150,
        required=True,
        widget=forms.TextInput(
            attrs={
                'readonly': 'readonly',
                'class': 'w-full rounded-md border-gray-300 shadow-sm bg-gray-100 cursor-not-allowed'
            }
        )
    )
    class Meta:
        model = Monitor
        fields = ['activo', 'estado', 'marca', 'modelo', 'n_serie', 'unive', 'bdo', 'ubicacion', 'asignado_a']
        widgets = {
            'estado': forms.Select(choices=opciones_estado),
            'marca': forms.TextInput(attrs={
                'class': 'w-full rounded-md shadow-sm border-gray-300',
                'placeholder': 'Escriba la marca'
            }),
            'ubicacion': forms.TextInput(attrs={ # Cambiado a TextInput
                'class': 'w-full rounded-md shadow-sm border-gray-300',
                'placeholder': 'Escriba la ubicación'
            }),
        }

    def clean_ubicacion(self): # Nueva función de limpieza para ubicación
        ubicacion = self.cleaned_data.get('ubicacion')
        if not ubicacion:
            raise forms.ValidationError('Este campo es obligatorio.')
        return ubicacion.strip()

    def clean_n_serie(self):
        n_serie = self.cleaned_data.get('n_serie')
        if Monitor.objects.exclude(id=self.instance.id).filter(n_serie=n_serie).exists():
            raise forms.ValidationError('Este Número de Serie ya existe para un Monitor.')
        return n_serie

    def clean_modelo(self):
        modelo = self.cleaned_data.get('modelo')
        if not modelo:
            raise forms.ValidationError('Este campo es obligatorio')
        return modelo

class AudioForm(forms.ModelForm):
    """
    Formulario para Equipos de Audio
    Incluye campo activo predeterminado y no editable
    """
    activo = forms.CharField(
        initial='Audio',
        max_length=150,
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'w-full rounded-md border-gray-300 shadow-sm'
            }
        )
    )
    class Meta:
        model = Audio
        fields = ['activo', 'estado', 'marca', 'modelo', 'n_serie', 'unive', 'bdo', 'ubicacion']
        widgets = {
            'estado': forms.Select(choices=opciones_estado),
            'marca': forms.TextInput(attrs={
                'class': 'w-full rounded-md shadow-sm border-gray-300',
                'list': 'marcas_list_audio', # ID único para el datalist de audio
                'placeholder': 'Seleccione o escriba una marca'
            }),
            'ubicacion': forms.TextInput(attrs={'placeholder': 'Ingrese la ubicación'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Establecer el valor inicial para 'marca' si estamos editando
        if self.instance and self.instance.pk:
            self.initial['marca'] = self.instance.marca

    def clean_marca(self):
        marca = self.cleaned_data.get('marca')
        if not marca:
            raise forms.ValidationError('Este campo es obligatorio.')
        return marca.strip()

    def clean_n_serie(self):
        n_serie = self.cleaned_data.get('n_serie')
        if Audio.objects.exclude(id=self.instance.id).filter(n_serie=n_serie).exists():
            raise forms.ValidationError('Este Número de Serie ya existe para un Equipo de Audio.')
        return n_serie

    def clean_modelo(self):
        modelo = self.cleaned_data.get('modelo')
        if not modelo:
            raise forms.ValidationError('Este campo es obligatorio')
        return modelo

    def clean_unive(self):
        unive = self.cleaned_data.get('unive')
        if Audio.objects.exclude(id=self.instance.id).filter(unive=unive).exists():
            raise forms.ValidationError('Este código UNIVE ya existe para un Equipo de Audio.')
        return unive


class TabletForm(forms.ModelForm):
    """
    Formulario para Tablets
    Incluye campo activo predeterminado y no editable
    """
    activo = forms.CharField(
        initial='Tablet',
        max_length=150,
        required=True,
        widget=forms.TextInput(
            attrs={
                'readonly': 'readonly',
                'class': 'w-full rounded-md border-gray-300 shadow-sm bg-gray-100 cursor-not-allowed'
            }
        )
    )
    netbios = forms.CharField(required=False, label='NetBIOS (Opcional)')


    class Meta:
        model = Tablet
        fields = ['activo', 'estado', 'marca', 'modelo', 'n_serie', 'unive', 'bdo', 'netbios', 'ubicacion']
        widgets = {
            'estado': forms.Select(choices=opciones_estado),
            'marca': forms.TextInput(attrs={
                'class': 'w-full rounded-md shadow-sm border-gray-300',
                'placeholder': 'Escriba la marca'
            }),
            'ubicacion': forms.TextInput(),
        }

    def clean_n_serie(self):
        n_serie = self.cleaned_data.get('n_serie')
        if Tablet.objects.exclude(id=self.instance.id).filter(n_serie=n_serie).exists():
            raise forms.ValidationError('Este Número de Serie ya existe para una Tablet.')
        return n_serie

    def clean_modelo(self):
        modelo = self.cleaned_data.get('modelo')
        if not modelo:
            raise forms.ValidationError('Este campo es obligatorio')
        return modelo
        
    def clean_unive(self):
        unive = self.cleaned_data.get('unive')
        if Tablet.objects.exclude(id=self.instance.id).filter(unive=unive).exists():
            raise forms.ValidationError('Este código UNIVE ya existe para una Tablet.')
        return unive
    
    def clean_netbios(self):
        netbios = self.cleaned_data.get('netbios')
        if netbios and Tablet.objects.exclude(id=self.instance.id).filter(netbios=netbios).exists():
            raise forms.ValidationError('Este NetBIOS ya existe para una Tablet.')
        return netbios

    def clean_activo(self):
        return 'Tablet'

#FORM PARA SUBIR ARCHIVOS EXCEL


class UploadExcelForm(forms.Form):
    excel_file = forms.FileField(
        label='Archivo Excel', 
        required=True,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )