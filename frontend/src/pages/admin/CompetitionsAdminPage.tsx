import React, { useEffect, useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import api from '../../api/client';
import type { Competition, Room, AdminRegistrationItem } from '../../types';
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

  // Room management state
  const [pendingRooms, setPendingRooms] = useState<{ name: string; capacity: number }[]>([]);
  const [existingRooms, setExistingRooms] = useState<Room[]>([]);
  const [newRoomName, setNewRoomName] = useState('');
  const [newRoomCapacity, setNewRoomCapacity] = useState(30);
  const [roomsLoading, setRoomsLoading] = useState(false);

  // Registrations modal state
  const [regModalOpen, setRegModalOpen] = useState(false);
  const [regCompetition, setRegCompetition] = useState<Competition | null>(null);
  const [regItems, setRegItems] = useState<AdminRegistrationItem[]>([]);
  const [regLoading, setRegLoading] = useState(false);
  const [participants, setParticipants] = useState<{ id: string; user_id: string; full_name: string; school: string }[]>([]);
  const [participantSearch, setParticipantSearch] = useState('');
  const [registering, setRegistering] = useState(false);

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

  const loadRooms = async (competitionId: string) => {
    setRoomsLoading(true);
    try {
      const { data } = await api.get<{ rooms: Room[] }>(`rooms/${competitionId}`);
      setExistingRooms(data.rooms || []);
    } catch {
      setExistingRooms([]);
    } finally {
      setRoomsLoading(false);
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
    setPendingRooms([]);
    setExistingRooms([]);
    setNewRoomName('');
    setNewRoomCapacity(30);
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
    setPendingRooms([]);
    setNewRoomName('');
    setNewRoomCapacity(30);
    setModalOpen(true);
    loadRooms(comp.id);
  };

  const addPendingRoom = () => {
    const name = newRoomName.trim();
    if (!name) return;
    if (pendingRooms.some((r) => r.name === name)) {
      setError('Аудитория с таким названием уже добавлена');
      return;
    }
    setPendingRooms((prev) => [...prev, { name, capacity: newRoomCapacity }]);
    setNewRoomName('');
    setNewRoomCapacity(30);
  };

  const removePendingRoom = (index: number) => {
    setPendingRooms((prev) => prev.filter((_, i) => i !== index));
  };

  const addExistingRoom = async () => {
    if (!editingId) return;
    const name = newRoomName.trim();
    if (!name) return;
    if (existingRooms.some((r) => r.name === name)) {
      setError('Аудитория с таким названием уже существует');
      return;
    }
    try {
      await api.post(`rooms/${editingId}`, { name, capacity: newRoomCapacity });
      setNewRoomName('');
      setNewRoomCapacity(30);
      await loadRooms(editingId);
    } catch (err: unknown) {
      const message =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
        'Не удалось добавить аудиторию.';
      setError(message);
    }
  };

  const deleteExistingRoom = async (roomId: string) => {
    if (!editingId) return;
    try {
      await api.delete(`rooms/room/${roomId}`);
      await loadRooms(editingId);
    } catch {
      setError('Не удалось удалить аудиторию.');
    }
  };

  const onSubmit = async (data: CompetitionForm) => {
    setSaving(true);
    setError(null);
    try {
      if (editingId) {
        await api.put(`competitions/${editingId}`, data);
      } else {
        const { data: newComp } = await api.post('competitions', data);
        // Create rooms for the new competition
        for (const room of pendingRooms) {
          await api.post(`rooms/${newComp.id}`, { name: room.name, capacity: room.capacity });
        }
      }
      setModalOpen(false);
      reset();
      setEditingId(null);
      setPendingRooms([]);
      setExistingRooms([]);
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

  const openRegModal = async (comp: Competition) => {
    setRegCompetition(comp);
    setRegModalOpen(true);
    setRegLoading(true);
    setParticipantSearch('');
    try {
      const [regRes, participantsRes] = await Promise.all([
        api.get<{ items: AdminRegistrationItem[]; total: number }>(`admin/registrations/${comp.id}`),
        api.get<{ participants: { id: string; user_id: string; full_name: string; school: string }[] }>('admin/participants'),
      ]);
      setRegItems(regRes.data.items || []);
      setParticipants(participantsRes.data.participants || []);
    } catch {
      try {
        const regRes = await api.get<{ items: AdminRegistrationItem[]; total: number }>(`admin/registrations/${comp.id}`);
        setRegItems(regRes.data.items || []);
      } catch {
        setError('Не удалось загрузить регистрации.');
      }
      setParticipants([]);
    } finally {
      setRegLoading(false);
    }
  };

  const handleAdminRegister = async (participantId: string) => {
    if (!regCompetition) return;
    setRegistering(true);
    setError(null);
    try {
      await api.post('admin/registrations', {
        participant_id: participantId,
        competition_id: regCompetition.id,
      });
      // Reload registrations
      const regRes = await api.get<{ items: AdminRegistrationItem[]; total: number }>(
        `admin/registrations/${regCompetition.id}`
      );
      setRegItems(regRes.data.items || []);
    } catch (err: unknown) {
      const message =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
        'Ошибка регистрации.';
      setError(message);
    } finally {
      setRegistering(false);
    }
  };

  const handleDownloadBadges = () => {
    if (!regCompetition) return;
    window.open(`/api/v1/admin/registrations/${regCompetition.id}/badges-pdf`, '_blank');
  };

  const getRegStatusLabel = (status: string): string => {
    const labels: Record<string, string> = {
      pending: 'Зарегистрирован',
      admitted: 'Допущен',
      completed: 'Завершен',
      cancelled: 'Отменен',
    };
    return labels[status] || status;
  };

  const filteredParticipants = participants.filter((p) => {
    // Exclude already registered
    if (regItems.some((r) => r.participant_id === p.id)) return false;
    if (!participantSearch) return true;
    const search = participantSearch.toLowerCase();
    return p.full_name.toLowerCase().includes(search) || p.school.toLowerCase().includes(search);
  });

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

  const handleAddRoom = () => {
    if (editingId) {
      addExistingRoom();
    } else {
      addPendingRoom();
    }
  };

  const roomsList = editingId ? existingRooms : pendingRooms;

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
                  <div className="flex gap-8 flex-wrap">
                    <Button
                      variant="secondary"
                      className="btn-sm"
                      onClick={() => openEdit(comp)}
                    >
                      Изменить
                    </Button>
                    <Button
                      variant="secondary"
                      className="btn-sm"
                      onClick={() => openRegModal(comp)}
                    >
                      Регистрации
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
          setPendingRooms([]);
          setExistingRooms([]);
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

          {/* Rooms section */}
          <div style={{ marginTop: 16, marginBottom: 16 }}>
            <label className="label" style={{ marginBottom: 8, display: 'block' }}>Аудитории</label>

            {/* Add room form */}
            <div style={{ display: 'flex', gap: 8, alignItems: 'flex-end' }}>
              <div style={{ flex: 1 }}>
                <Input
                  label="Название"
                  value={newRoomName}
                  onChange={(e) => setNewRoomName(e.target.value)}
                />
              </div>
              <div style={{ width: 100 }}>
                <Input
                  label="Мест"
                  type="number"
                  min={1}
                  value={newRoomCapacity}
                  onChange={(e) => setNewRoomCapacity(Number(e.target.value))}
                />
              </div>
              <Button
                type="button"
                variant="secondary"
                onClick={handleAddRoom}
                style={{ marginBottom: 16 }}
              >
                Добавить
              </Button>
            </div>

            {/* Rooms list */}
            {roomsLoading ? (
              <p className="text-muted">Загрузка аудиторий...</p>
            ) : roomsList.length > 0 ? (
              <div
                style={{
                  border: '1px solid var(--glass-border, #e2e8f0)',
                  borderRadius: 8,
                  overflow: 'hidden',
                  marginTop: 4,
                }}
              >
                {roomsList.map((room, index) => (
                  <div
                    key={'id' in room ? (room as Room).id : index}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      padding: '8px 12px',
                      borderBottom:
                        index < roomsList.length - 1
                          ? '1px solid var(--glass-border, #e2e8f0)'
                          : 'none',
                      background: index % 2 === 0 ? 'var(--glass-surface, #f8fafc)' : 'transparent',
                    }}
                  >
                    <span>
                      <strong>{index + 1}.</strong> {room.name}
                      <span className="text-muted" style={{ marginLeft: 8 }}>
                        ({room.capacity} мест)
                      </span>
                    </span>
                    <Button
                      type="button"
                      variant="danger"
                      className="btn-sm"
                      onClick={() =>
                        editingId
                          ? deleteExistingRoom((room as Room).id)
                          : removePendingRoom(index)
                      }
                    >
                      Удалить
                    </Button>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-muted" style={{ marginTop: 4, fontSize: 13 }}>
                Аудитории не добавлены
              </p>
            )}
          </div>

          <Button type="submit" loading={saving} style={{ width: '100%' }}>
            {editingId ? 'Сохранить' : 'Создать'}
          </Button>
        </form>
      </Modal>

      {/* Registrations Modal */}
      <Modal
        isOpen={regModalOpen}
        onClose={() => {
          setRegModalOpen(false);
          setRegCompetition(null);
          setRegItems([]);
          setParticipants([]);
          setParticipantSearch('');
        }}
        title={`Регистрации — ${regCompetition?.name || ''}`}
      >
        {regLoading ? (
          <Spinner />
        ) : (
          <div>
            {/* Download badges button */}
            {regItems.length > 0 && (
              <div style={{ marginBottom: 16 }}>
                <Button variant="secondary" onClick={handleDownloadBadges}>
                  Скачать бейджи PDF
                </Button>
              </div>
            )}

            {/* Registrations table */}
            {regItems.length > 0 ? (
              <div style={{ maxHeight: 300, overflowY: 'auto', marginBottom: 24 }}>
                <table className="table" style={{ fontSize: 13 }}>
                  <thead>
                    <tr>
                      <th>ФИО</th>
                      <th>Школа</th>
                      <th>Учреждение</th>
                      <th>Статус</th>
                    </tr>
                  </thead>
                  <tbody>
                    {regItems.map((item) => (
                      <tr key={item.registration_id}>
                        <td>{item.participant_name}</td>
                        <td>{item.participant_school}</td>
                        <td>{item.institution_name || '—'}</td>
                        <td>{getRegStatusLabel(item.status)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <p className="text-muted" style={{ marginBottom: 16 }}>Регистраций пока нет.</p>
            )}

            {/* Register new participant */}
            <h3 style={{ marginBottom: 8 }}>Зарегистрировать участника</h3>
            <Input
              label="Поиск участника"
              value={participantSearch}
              onChange={(e) => setParticipantSearch(e.target.value)}
              placeholder="Введите ФИО или школу..."
            />
            {participants.length > 0 && (
              <div style={{ maxHeight: 200, overflowY: 'auto', border: '1px solid var(--glass-border, #e2e8f0)', borderRadius: 8, marginTop: 4 }}>
                {filteredParticipants.length === 0 ? (
                  <p className="text-muted" style={{ padding: 12 }}>Не найдено подходящих участников.</p>
                ) : (
                  filteredParticipants.slice(0, 20).map((p) => (
                    <div
                      key={p.id}
                      style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        padding: '8px 12px',
                        borderBottom: '1px solid var(--glass-border, #e2e8f0)',
                      }}
                    >
                      <span>
                        <strong>{p.full_name}</strong>
                        <span className="text-muted" style={{ marginLeft: 8, fontSize: 12 }}>
                          {p.school}
                        </span>
                      </span>
                      <Button
                        className="btn-sm"
                        onClick={() => handleAdminRegister(p.id)}
                        loading={registering}
                      >
                        Зарегистрировать
                      </Button>
                    </div>
                  ))
                )}
              </div>
            )}
            {participants.length === 0 && !regLoading && (
              <p className="text-muted" style={{ marginTop: 8, fontSize: 13 }}>
                Не удалось загрузить список участников.
              </p>
            )}
          </div>
        )}
      </Modal>
    </Layout>
  );
};

export default CompetitionsAdminPage;
