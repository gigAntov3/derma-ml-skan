from fastapi import HTTPException, status
from dataclasses import dataclass
from typing import Tuple, Optional, List

from utils.database.uow import UnitOfWork
from models.users import User
from api.schemas.users import UserResponse, UserUpdateRequest, UserAdminUpdateRequest


@dataclass
class UsersService:
    """Сервис для работы с пользователями"""
    
    uow: UnitOfWork

    async def get_me(self, user_id: int) -> UserResponse:
        """Получает информацию о текущем пользователе"""
        async with self.uow as uow:
            user = await uow.users.get_by_id(user_id)
            
            if not user:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
            
            if not user.is_active:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not active")
        
        return UserResponse(
            id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            middle_name=user.middle_name,
            email=user.email,
            phone=user.phone,
            birth_date=user.birth_date,
            roles=[role.code for role in user.roles],
            is_active=user.is_active,
            created_at=user.created_at
        )
    
    async def update_user(self, user_id: int, update_data: UserUpdateRequest) -> UserResponse:
        """Обновляет данные пользователя"""
        async with self.uow as uow:
            # Проверяем, существует ли пользователь
            user = await uow.users.get_by_id(user_id)
            if not user:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
            
            if not user.is_active:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not active")
            
            # Проверяем уникальность phone, если он меняется
            if update_data.phone and update_data.phone != user.phone:
                existing_user = await uow.users.get_by_phone(update_data.phone)
                if existing_user and existing_user.id != user_id:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Phone number already exists"
                    )
            
            # Проверяем уникальность email, если он меняется
            if update_data.email and update_data.email != user.email:
                existing_user = await uow.users.get_by_email(update_data.email)
                if existing_user and existing_user.id != user_id:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Email already exists"
                    )
            
            # Подготавливаем данные для обновления (исключаем None значения)
            update_dict = update_data.model_dump(exclude_unset=True)
            
            # Обновляем пользователя
            updated_user = await uow.users.update_user(user_id, update_dict)
            
            if not updated_user:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to update user"
                )
            
            # Сохраняем изменения
            await uow.commit()
        
        # Возвращаем обновленные данные
        return UserResponse(
            id=updated_user.id,
            first_name=updated_user.first_name,
            last_name=updated_user.last_name,
            middle_name=updated_user.middle_name,
            email=updated_user.email,
            phone=updated_user.phone,
            birth_date=updated_user.birth_date,
            roles=[role.code for role in updated_user.roles],
            is_active=updated_user.is_active,
            created_at=updated_user.created_at
        )
    
    async def get_all_users(
        self, 
        role: Optional[str] = None, 
        offset: int = 0, 
        limit: int = 100
    ) -> List[UserResponse]:
        """Получает всех пользователей (только для админа)"""
        async with self.uow as uow:
            users = await uow.users.get_all(role=role, offset=offset, limit=limit)
        
        return [
            UserResponse(
                id=user.id,
                first_name=user.first_name,
                last_name=user.last_name,
                middle_name=user.middle_name,
                email=user.email,
                phone=user.phone,
                birth_date=user.birth_date,
                roles=[role.code for role in user.roles],
                is_active=user.is_active,
                created_at=user.created_at
            )
            for user in users
        ]

    async def get_user_by_id(self, user_id: int) -> UserResponse:
        """Получает пользователя по ID (только для админа)"""
        async with self.uow as uow:
            user = await uow.users.get_by_id(user_id)
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, 
                    detail="User not found"
                )
        
        return UserResponse(
            id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            middle_name=user.middle_name,
            email=user.email,
            phone=user.phone,
            birth_date=user.birth_date,
            roles=[role.code for role in user.roles],
            is_active=user.is_active,
            created_at=user.created_at
        )

    async def admin_update_user(
        self, 
        user_id: int, 
        update_data: UserAdminUpdateRequest,
    ) -> UserResponse:
        """Обновляет пользователя от имени администратора"""
        async with self.uow as uow:
            # Проверяем, существует ли пользователь
            user = await uow.users.get_by_id(user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, 
                    detail="User not found"
                )
            
            # Подготавливаем данные для обновления
            update_dict = update_data.model_dump(exclude_unset=True)
            
            # Проверяем уникальность полей, если они меняются
            if 'email' in update_dict and update_dict['email'] != user.email:
                existing_user = await uow.users.get_by_email(update_dict['email'])
                if existing_user and existing_user.id != user_id:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Email already exists"
                    )
            
            if 'phone' in update_dict and update_dict['phone'] != user.phone:
                existing_user = await uow.users.get_by_phone(update_dict['phone'])
                if existing_user and existing_user.id != user_id:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Phone number already exists"
                    )
            
            # Обрабатываем обновление ролей отдельно
            roles_to_update = update_dict.pop('roles', None)
            
            # Обновляем основные поля
            if update_dict:
                updated_user = await uow.users.update_user(user_id, update_dict)
                if not updated_user:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Failed to update user"
                    )
            else:
                updated_user = user
            
            # Обновляем роли, если они переданы
            if roles_to_update is not None:
                await uow.users.update_user_roles(user_id, roles_to_update)
            
            # Сохраняем изменения
            await uow.commit()
            
            # Получаем обновленного пользователя с новыми ролями
            final_user = await uow.users.get_by_id(user_id)
        
        return UserResponse(
            id=final_user.id,
            first_name=final_user.first_name,
            last_name=final_user.last_name,
            middle_name=final_user.middle_name,
            email=final_user.email,
            phone=final_user.phone,
            birth_date=final_user.birth_date,
            roles=[role.code for role in final_user.roles],
            is_active=final_user.is_active,
            created_at=final_user.created_at
        )
    
    async def delete_user(self, user_id: int) -> dict:
        """
        Удаляет пользователя (только для админа)
        """
        async with self.uow as uow:
            # Проверяем, существует ли пользователь
            user = await uow.users.get_by_id(user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            # Удаляем пользователя
            await uow.users.delete(user_id)
            await uow.commit()
        
        return {"message": f"User {user_id} deleted successfully"}
    
    async def get_user_roles(self, user_id: int) -> List[str]:
        """Получает роли пользователя"""
        async with self.uow as uow:
            user = await uow.users.get_by_id(user_id)
            if not user:
                return []
            
            return [role.code for role in user.roles]
    
    async def update_user_status(
        self, 
        user_id: int, 
        is_active: bool
    ) -> UserResponse:
        """Обновляет статус активности пользователя (только для админа)"""
        async with self.uow as uow:
            # Проверяем, существует ли пользователь
            user = await uow.users.get_by_id(user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            # Обновляем статус
            updated_user = await uow.users.update_user(user_id, {"is_active": is_active})
            
            if not updated_user:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to update user status"
                )
            
            await uow.commit()
        
        return UserResponse(
            id=updated_user.id,
            first_name=updated_user.first_name,
            last_name=updated_user.last_name,
            middle_name=updated_user.middle_name,
            email=updated_user.email,
            phone=updated_user.phone,
            birth_date=updated_user.birth_date,
            roles=[role.code for role in updated_user.roles],
            is_active=updated_user.is_active,
            created_at=updated_user.created_at
        )
    
    async def get_patients_list(
        self, 
        offset: int = 0, 
        limit: int = 100
    ) -> List[UserResponse]:
        """Получает список всех пациентов"""
        async with self.uow as uow:
            patients = await uow.users.get_by_role("patient", offset=offset, limit=limit)
        
        return [
            UserResponse(
                id=patient.id,
                first_name=patient.first_name,
                last_name=patient.last_name,
                middle_name=patient.middle_name,
                email=patient.email,
                phone=patient.phone,
                birth_date=patient.birth_date,
                roles=[role.code for role in patient.roles],
                is_active=patient.is_active,
                created_at=patient.created_at
            )
            for patient in patients
        ]
    
    async def get_doctors_list(
        self, 
        offset: int = 0, 
        limit: int = 100
    ) -> List[UserResponse]:
        """Получает список всех врачей"""
        async with self.uow as uow:
            doctors = await uow.users.get_by_role("doctor", offset=offset, limit=limit)
        
        return [
            UserResponse(
                id=doctor.id,
                first_name=doctor.first_name,
                last_name=doctor.last_name,
                middle_name=doctor.middle_name,
                email=doctor.email,
                phone=doctor.phone,
                birth_date=doctor.birth_date,
                roles=[role.code for role in doctor.roles],
                is_active=doctor.is_active,
                created_at=doctor.created_at
            )
            for doctor in doctors
        ]