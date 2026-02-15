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
  password: z.string().min(8, 'Минимум 8 символов'),
  role: z.enum(['participant', 'admitter', 'scanner', 'admin']),
  full_name: z.string().optional(),
  school: z.string().optional(),
  grade: z.preprocess(
    (val) => (typeof val === 'number' && isNaN(val) ? undefined : val),
    z.number().optional()
  ),
}).refine((data) => {
  // For participants, full_name, school, and grade are required
  if (data.role === 'participant') {
    if (!data.full_name || data.full_name.trim().length < 2) {
      return false;
    }
    if (!data.school || data.school.trim().length < 2) {
      return false;
    }
    if (!data.grade || data.grade < 1 || data.grade > 12) {
      return false;
    }
  }
  return true;
}, {
  message: 'Для участників необходимо указать ФИО, школу и класс (минимум 2 символа для текста, класс 1-12)',
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
    console.log('handleCreate called with data:', data);
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

      console.log('Sending request with cleanData:', cleanData);
      const response = await api.post('admin/users', cleanData);
      console.log('User created successfully:', response.data);
      setModalOpen(false);
      reset();
      await loadUsers();
    } catch (err: unknown) {
      console.error('Error creating user:', err);
      const message =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
        'Не удалось создать пользователя.';
      console.error('Error message:', message);
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
        <form onSubmit={handleSubmit(handleCreate, (errors) => {
          console.error('Form validation errors:', errors);
        })}>
          {error && <div className="alert alert-error mb-16">{error}</div>}
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
