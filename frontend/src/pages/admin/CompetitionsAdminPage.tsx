import React, { useEffect, useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import api from '../../api/client';
import type { Competition } from '../../types';
import Layout from '../../components/layout/Layout';
import Button from '../../components/common/Button';
import Input from '../../components/common/Input';
import Modal from '../../components/common/Modal';
import Spinner from '../../components/common/Spinner';

const competitionSchema = z.object({
  name: z.string().min(1, 'Название обязательно'),
  date: z.string().min(1, 'Дата обязательна'),
  registration_start: z.string().min(1, 'Обязательное поле'),
  registration_end: z.string().min(1, 'Обязательное поле'),
  variants_count: z.coerce.number().min(1, 'Минимум 1 вариант'),
  max_score: z.coerce.number().min(1, 'Должно быть положительным'),
});

type CompetitionForm = z.infer<typeof competitionSchema>;

const CompetitionsAdminPage: React.FC = () => {
  const [competitions, setCompetitions] = useState<Competition[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [saving, setSaving] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    reset,
    setValue,
    formState: { errors },
  } = useForm<CompetitionForm>({
    resolver: zodResolver(competitionSchema),
  });

  useEffect(() => {
    loadCompetitions();
  }, []);

  const loadCompetitions = async () => {
    setLoading(true);
    try {
      const { data } = await api.get<{ competitions: Competition[]; total: number }>('competitions');
      setCompetitions(data.competitions || []);
    } catch {
      setError('Не удалось загрузить олимпиады.');
    } finally {
      setLoading(false);
    }
  };

  const openCreate = () => {
    setEditingId(null);
    reset({
      name: '',
      date: '',
      registration_start: '',
      registration_end: '',
      variants_count: 4,
      max_score: 100,
    });
    setModalOpen(true);
  };

  const openEdit = (comp: Competition) => {
    setEditingId(comp.id);
    setValue('name', comp.name);
    setValue('date', comp.date.slice(0, 10));
    setValue('registration_start', comp.registration_start.slice(0, 16));
    setValue('registration_end', comp.registration_end.slice(0, 16));
    setValue('variants_count', comp.variants_count);
    setValue('max_score', comp.max_score);
    setModalOpen(true);
  };

  const onSubmit = async (data: CompetitionForm) => {
    setSaving(true);
    setError(null);
    try {
      if (editingId) {
        await api.put(`competitions/${editingId}`, data);
      } else {
        await api.post('competitions', data);
      }
      setModalOpen(false);
      reset();
      setEditingId(null);
      await loadCompetitions();
    } catch (err: unknown) {
      const message =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
        'Не удалось сохранить олимпиаду.';
      setError(message);
    } finally {
      setSaving(false);
    }
  };

  const handleStatusChange = async (id: string, action: string) => {
    try {
      await api.post(`competitions/${id}/${action}`);
      await loadCompetitions();
    } catch {
      setError('Не удалось обновить статус.');
    }
  };

  const getStatusLabel = (status: string): string => {
    const labels: Record<string, string> = {
      draft: 'Черновик',
      registration_open: 'Регистрация открыта',
      in_progress: 'Проходит',
      checking: 'Проверка',
      published: 'Опубликована',
    };
    return labels[status] || status;
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
        <h1>Олимпиады</h1>
        <Button onClick={openCreate}>Создать олимпиаду</Button>
      </div>

      {error && <div className="alert alert-error mb-16">{error}</div>}

      <table className="table">
        <thead>
          <tr>
            <th>Название</th>
            <th>Дата</th>
            <th>Статус</th>
            <th>Варианты</th>
            <th>Макс. балл</th>
            <th>Действия</th>
          </tr>
        </thead>
        <tbody>
          {competitions.length === 0 ? (
            <tr>
              <td colSpan={6} className="text-center text-muted">
                Олимпиад пока нет.
              </td>
            </tr>
          ) : (
            competitions.map((comp) => (
              <tr key={comp.id}>
                <td>{comp.name}</td>
                <td>{new Date(comp.date).toLocaleDateString('ru-RU')}</td>
                <td>{getStatusLabel(comp.status)}</td>
                <td>{comp.variants_count}</td>
                <td>{comp.max_score}</td>
                <td>
                  <div className="flex gap-8">
                    <Button
                      variant="secondary"
                      className="btn-sm"
                      onClick={() => openEdit(comp)}
                    >
                      Изменить
                    </Button>
                    {comp.status === 'draft' && (
                      <Button
                        className="btn-sm"
                        onClick={() => handleStatusChange(comp.id, 'open-registration')}
                      >
                        Открыть рег.
                      </Button>
                    )}
                    {comp.status === 'registration_open' && (
                      <Button
                        variant="secondary"
                        className="btn-sm"
                        onClick={() => handleStatusChange(comp.id, 'start')}
                      >
                        Начать
                      </Button>
                    )}
                    {comp.status === 'in_progress' && (
                      <Button
                        variant="danger"
                        className="btn-sm"
                        onClick={() => handleStatusChange(comp.id, 'start-checking')}
                      >
                        Завершить
                      </Button>
                    )}
                    {comp.status === 'checking' && (
                      <Button
                        variant="success"
                        className="btn-sm"
                        onClick={() => handleStatusChange(comp.id, 'publish')}
                      >
                        Опубликовать
                      </Button>
                    )}
                  </div>
                </td>
              </tr>
            ))
          )}
        </tbody>
      </table>

      <Modal
        isOpen={modalOpen}
        onClose={() => {
          setModalOpen(false);
          reset();
          setEditingId(null);
        }}
        title={editingId ? 'Редактировать олимпиаду' : 'Создать олимпиаду'}
      >
        <form onSubmit={handleSubmit(onSubmit)}>
          <Input
            label="Название"
            error={errors.name?.message}
            {...register('name')}
          />
          <Input
            label="Дата проведения"
            type="date"
            error={errors.date?.message}
            {...register('date')}
          />
          <Input
            label="Начало регистрации"
            type="datetime-local"
            error={errors.registration_start?.message}
            {...register('registration_start')}
          />
          <Input
            label="Конец регистрации"
            type="datetime-local"
            error={errors.registration_end?.message}
            {...register('registration_end')}
          />
          <Input
            label="Количество вариантов"
            type="number"
            min={1}
            error={errors.variants_count?.message}
            {...register('variants_count')}
          />
          <Input
            label="Максимальный балл"
            type="number"
            min={1}
            error={errors.max_score?.message}
            {...register('max_score')}
          />
          <Button type="submit" loading={saving} style={{ width: '100%' }}>
            {editingId ? 'Сохранить' : 'Создать'}
          </Button>
        </form>
      </Modal>
    </Layout>
  );
};

export default CompetitionsAdminPage;
