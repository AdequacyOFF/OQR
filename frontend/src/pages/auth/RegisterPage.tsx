import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Link, useNavigate } from 'react-router-dom';
import useAuthStore from '../../store/authStore';
import Input from '../../components/common/Input';
import Button from '../../components/common/Button';

const registerSchema = z.object({
  email: z.string().email('Invalid email address'),
  password: z.string().min(6, 'Password must be at least 6 characters'),
  role: z.enum(['participant', 'admitter', 'scanner', 'admin'], {
    required_error: 'Please select a role',
  }),
  full_name: z.string().min(1, 'Full name is required'),
  school: z.string().optional(),
  grade: z.coerce.number().min(1).max(12).optional(),
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
    watch,
    formState: { errors },
  } = useForm<RegisterForm>({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      role: 'participant',
    },
  });

  const selectedRole = watch('role');

  const onSubmit = async (data: RegisterForm) => {
    setError(null);
    setLoading(true);
    try {
      await registerUser({
        email: data.email,
        password: data.password,
        role: data.role,
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
        'Registration failed. Please try again.';
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-wrapper">
      <div className="card auth-card">
        <h1>Register</h1>
        {error && <div className="alert alert-error">{error}</div>}
        <form onSubmit={handleSubmit(onSubmit)}>
          <Input
            label="Full Name"
            placeholder="John Doe"
            error={errors.full_name?.message}
            {...register('full_name')}
          />
          <Input
            label="Email"
            type="email"
            placeholder="you@example.com"
            error={errors.email?.message}
            {...register('email')}
          />
          <Input
            label="Password"
            type="password"
            placeholder="At least 6 characters"
            error={errors.password?.message}
            {...register('password')}
          />
          <div className="form-group">
            <label htmlFor="role">Role</label>
            <select
              id="role"
              className="input"
              {...register('role')}
            >
              <option value="participant">Participant</option>
              <option value="admitter">Admitter</option>
              <option value="scanner">Scanner</option>
              <option value="admin">Admin</option>
            </select>
            {errors.role && <p className="error-text">{errors.role.message}</p>}
          </div>
          {selectedRole === 'participant' && (
            <>
              <Input
                label="School"
                placeholder="Your school name"
                error={errors.school?.message}
                {...register('school')}
              />
              <Input
                label="Grade"
                type="number"
                placeholder="1-12"
                min={1}
                max={12}
                error={errors.grade?.message}
                {...register('grade')}
              />
            </>
          )}
          <Button type="submit" loading={loading} style={{ width: '100%' }}>
            Register
          </Button>
        </form>
        <p className="text-center mt-16 text-muted">
          Already have an account? <Link to="/login">Sign In</Link>
        </p>
      </div>
    </div>
  );
};

export default RegisterPage;
