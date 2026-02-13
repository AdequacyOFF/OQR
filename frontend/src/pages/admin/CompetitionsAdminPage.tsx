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
  name: z.string().min(1, 'Name is required'),
  date: z.string().min(1, 'Date is required'),
  registration_start: z.string().min(1, 'Required'),
  registration_end: z.string().min(1, 'Required'),
  variants_count: z.coerce.number().min(1, 'At least 1 variant'),
  max_score: z.coerce.number().min(1, 'Must be positive'),
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
      const { data } = await api.get<Competition[]>('/competitions');
      setCompetitions(data);
    } catch {
      setError('Failed to load competitions.');
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
    setValue('date', comp.date.slice(0, 16));
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
        await api.put(`/competitions/${editingId}`, data);
      } else {
        await api.post('/competitions', data);
      }
      setModalOpen(false);
      reset();
      setEditingId(null);
      await loadCompetitions();
    } catch (err: unknown) {
      const message =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
        'Failed to save competition.';
      setError(message);
    } finally {
      setSaving(false);
    }
  };

  const handleStatusChange = async (id: string, status: string) => {
    try {
      await api.put(`/competitions/${id}`, { status });
      await loadCompetitions();
    } catch {
      setError('Failed to update status.');
    }
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
        <h1>Competitions</h1>
        <Button onClick={openCreate}>Create Competition</Button>
      </div>

      {error && <div className="alert alert-error mb-16">{error}</div>}

      <table className="table">
        <thead>
          <tr>
            <th>Name</th>
            <th>Date</th>
            <th>Status</th>
            <th>Variants</th>
            <th>Max Score</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {competitions.length === 0 ? (
            <tr>
              <td colSpan={6} className="text-center text-muted">
                No competitions yet.
              </td>
            </tr>
          ) : (
            competitions.map((comp) => (
              <tr key={comp.id}>
                <td>{comp.name}</td>
                <td>{new Date(comp.date).toLocaleDateString()}</td>
                <td>{comp.status}</td>
                <td>{comp.variants_count}</td>
                <td>{comp.max_score}</td>
                <td>
                  <div className="flex gap-8">
                    <Button
                      variant="secondary"
                      className="btn-sm"
                      onClick={() => openEdit(comp)}
                    >
                      Edit
                    </Button>
                    {comp.status === 'draft' && (
                      <Button
                        className="btn-sm"
                        onClick={() => handleStatusChange(comp.id, 'registration_open')}
                      >
                        Open Reg
                      </Button>
                    )}
                    {comp.status === 'registration_open' && (
                      <Button
                        variant="secondary"
                        className="btn-sm"
                        onClick={() => handleStatusChange(comp.id, 'in_progress')}
                      >
                        Start
                      </Button>
                    )}
                    {comp.status === 'in_progress' && (
                      <Button
                        variant="danger"
                        className="btn-sm"
                        onClick={() => handleStatusChange(comp.id, 'finished')}
                      >
                        Finish
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
        title={editingId ? 'Edit Competition' : 'Create Competition'}
      >
        <form onSubmit={handleSubmit(onSubmit)}>
          <Input
            label="Name"
            error={errors.name?.message}
            {...register('name')}
          />
          <Input
            label="Date"
            type="datetime-local"
            error={errors.date?.message}
            {...register('date')}
          />
          <Input
            label="Registration Start"
            type="datetime-local"
            error={errors.registration_start?.message}
            {...register('registration_start')}
          />
          <Input
            label="Registration End"
            type="datetime-local"
            error={errors.registration_end?.message}
            {...register('registration_end')}
          />
          <Input
            label="Variants Count"
            type="number"
            min={1}
            error={errors.variants_count?.message}
            {...register('variants_count')}
          />
          <Input
            label="Max Score"
            type="number"
            min={1}
            error={errors.max_score?.message}
            {...register('max_score')}
          />
          <Button type="submit" loading={saving} style={{ width: '100%' }}>
            {editingId ? 'Update' : 'Create'}
          </Button>
        </form>
      </Modal>
    </Layout>
  );
};

export default CompetitionsAdminPage;
