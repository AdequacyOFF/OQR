import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Link, useNavigate } from 'react-router-dom';
import useAuthStore from '../../store/authStore';
import Input from '../../components/common/Input';
import Button from '../../components/common/Button';

const registerSchema = z.object({
  email: z.string().email('Введите корректный email'),
  password: z.string().min(6, 'Пароль должен содержать минимум 6 символов'),
  full_name: z.string().min(1, 'Введите ФИО'),
  school: z.string().min(1, 'Введите название школы'),
  grade: z.coerce.number().min(1, 'Минимум 1').max(12, 'Максимум 12'),
});

type RegisterForm = z.infer<typeof registerSchema>;

const roleRedirects: Record<string, string> = {
  participant: '/dashboard',
  admitter: '/admission',
  scanner: '/scans',
  admin: '/admin',
};

const RegisterPage: React.FC = () => {
  const { register: registerUser } = useAuthStore();
  const navigate = useNavigate();
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<RegisterForm>({
    resolver: zodResolver(registerSchema),
  });

  const onSubmit = async (data: RegisterForm) => {
    setError(null);
    setLoading(true);
    try {
      await registerUser({
        email: data.email,
        password: data.password,
        role: 'participant',
        full_name: data.full_name,
        school: data.school,
        grade: data.grade,
      });
      const user = useAuthStore.getState().user;
      const redirect = user ? roleRedirects[user.role] || '/dashboard' : '/dashboard';
      navigate(redirect);
    } catch (err: unknown) {
      const message =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
        'Ошибка регистрации. Попробуйте снова.';
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-wrapper">
      <div className="card auth-card">
        <h1>Регистрация</h1>
        {error && <div className="alert alert-error">{error}</div>}
        <form onSubmit={handleSubmit(onSubmit)}>
          <Input
            label="ФИО"
            placeholder="Иванов Иван Иванович"
            error={errors.full_name?.message}
            {...register('full_name')}
          />
          <Input
            label="Email"
            type="email"
            placeholder="example@mail.ru"
            error={errors.email?.message}
            {...register('email')}
          />
          <Input
            label="Пароль"
            type="password"
            placeholder="Минимум 6 символов"
            error={errors.password?.message}
            {...register('password')}
          />
          <Input
            label="Школа"
            placeholder="Название школы"
            error={errors.school?.message}
            {...register('school')}
          />
          <Input
            label="Класс"
            type="number"
            placeholder="1-12"
            min={1}
            max={12}
            error={errors.grade?.message}
            {...register('grade')}
          />
          <Button type="submit" loading={loading} style={{ width: '100%' }}>
            Зарегистрироваться
          </Button>
        </form>
        <p className="text-center mt-16 text-muted">
          Уже есть аккаунт? <Link to="/login">Войти</Link>
        </p>
      </div>
    </div>
  );
};

export default RegisterPage;
