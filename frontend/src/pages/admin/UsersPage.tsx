import React, { useEffect, useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import api from '../../api/client';
import type { UserInfo } from '../../types';
import Layout from '../../components/layout/Layout';
import Button from '../../components/common/Button';
import Input from '../../components/common/Input';
import Modal from '../../components/common/Modal';
import Spinner from '../../components/common/Spinner';

const createUserSchema = z.object({
  email: z.string().email('Введите корректный email'),
  password: z.string().min(6, 'Минимум 6 символов'),
  role: z.enum(['participant', 'admitter', 'scanner', 'admin']),
  full_name: z.string().min(2, 'Минимум 2 символа').optional(),
  school: z.string().min(2, 'Минимум 2 символа').optional(),
  grade: z.number().min(1, 'Класс от 1 до 12').max(12, 'Класс от 1 до 12').optional(),
}).refine((data) => {
  // For participants, full_name, school, and grade are required
  if (data.role === 'participant') {
    return data.full_name && data.school && data.grade;
  }
  return true;
}, {
  message: 'Для участников необходимо указать ФИО, школу и класс',
  path: ['full_name'],
});

type CreateUserForm = z.infer<typeof createUserSchema>;

const UsersPage: React.FC = () => {
  const [users, setUsers] = useState<UserInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [creating, setCreating] = useState(false);

  const {
    register,
    handleSubmit,
    reset,
    watch,
    formState: { errors },
  } = useForm<CreateUserForm>({
    resolver: zodResolver(createUserSchema),
    defaultValues: { role: 'participant' },
  });

  const selectedRole = watch('role');

  useEffect(() => {
    loadUsers();
  }, []);

  const loadUsers = async () => {
    setLoading(true);
    try {
      const { data } = await api.get<{ items: UserInfo[]; total: number }>('admin/users');
      setUsers(data.items || []);
    } catch {
      setError('Не удалось загрузить пользователей.');
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (data: CreateUserForm) => {
    setCreating(true);
    setError(null);
    try {
      // Clean data - remove participant fields for non-participant roles
      const cleanData: any = {
        email: data.email,
        password: data.password,
        role: data.role,
      };

      // Only include participant fields if role is participant
      if (data.role === 'participant') {
        cleanData.full_name = data.full_name;
        cleanData.school = data.school;
        cleanData.grade = data.grade;
      }

      await api.post('admin/users', cleanData);
      setModalOpen(false);
      reset();
      await loadUsers();
    } catch (err: unknown) {
      const message =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
        'Не удалось создать пользователя.';
      setError(message);
    } finally {
      setCreating(false);
    }
  };

  const handleToggleActive = async (user: UserInfo) => {
    try {
      await api.put(`admin/users/${user.id}`, {
        is_active: !user.is_active,
      });
      await loadUsers();
    } catch {
      setError('Не удалось обновить пользователя.');
    }
  };

  const getRoleLabel = (role: string): string => {
    const labels: Record<string, string> = {
      participant: 'Участник',
      admitter: 'Допуск',
      scanner: 'Сканер',
      admin: 'Администратор',
    };
    return labels[role] || role;
  };

  if (loading) {
    return (
      <Layout>
        <Spinner />
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="flex-between mb-24">
        <h1>Пользователи</h1>
        <Button onClick={() => setModalOpen(true)}>Создать пользователя</Button>
      </div>

      {error && <div className="alert alert-error mb-16">{error}</div>}

      <table className="table">
        <thead>
          <tr>
            <th>Email</th>
            <th>Роль</th>
            <th>Активен</th>
            <th>Действия</th>
          </tr>
        </thead>
        <tbody>
          {users.map((user) => (
            <tr key={user.id}>
              <td>{user.email}</td>
              <td>{getRoleLabel(user.role)}</td>
              <td>{user.is_active ? 'Да' : 'Нет'}</td>
              <td>
                <Button
                  variant={user.is_active ? 'danger' : 'primary'}
                  className="btn-sm"
                  onClick={() => handleToggleActive(user)}
                >
                  {user.is_active ? 'Деактивировать' : 'Активировать'}
                </Button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      <Modal
        isOpen={modalOpen}
        onClose={() => {
          setModalOpen(false);
          reset();
        }}
        title="Создать пользователя"
      >
        <form onSubmit={handleSubmit(handleCreate)}>
          <Input
            label="Email"
            type="email"
            error={errors.email?.message}
            {...register('email')}
          />
          <Input
            label="Пароль"
            type="password"
            error={errors.password?.message}
            {...register('password')}
          />
          <div className="form-group">
            <label htmlFor="create-role">Роль</label>
            <select id="create-role" className="input" {...register('role')}>
              <option value="participant">Участник</option>
              <option value="admitter">Допуск</option>
              <option value="scanner">Сканер</option>
              <option value="admin">Администратор</option>
            </select>
            {errors.role && <p className="error-text">{errors.role.message}</p>}
          </div>

          {selectedRole === 'participant' && (
            <>
              <Input
                label="ФИО *"
                error={errors.full_name?.message}
                {...register('full_name')}
              />
              <Input
                label="Школа *"
                error={errors.school?.message}
                {...register('school')}
              />
              <Input
                label="Класс (1-12) *"
                type="number"
                error={errors.grade?.message}
                {...register('grade', { valueAsNumber: true })}
              />
            </>
          )}

          <Button type="submit" loading={creating} style={{ width: '100%' }}>
            Создать
          </Button>
        </form>
      </Modal>
    </Layout>
  );
};

export default UsersPage;
