import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import api from '../../api/client';
import Layout from '../../components/layout/Layout';
import Button from '../../components/common/Button';
import type { Room, Competition } from '../../types';

const RoomsPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const competitionId = searchParams.get('competition_id');

  const [competitions, setCompetitions] = useState<Competition[]>([]);
  const [selectedCompetition, setSelectedCompetition] = useState<string>(competitionId || '');
  const [rooms, setRooms] = useState<Room[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [formName, setFormName] = useState('');
  const [formCapacity, setFormCapacity] = useState('');
  const [creating, setCreating] = useState(false);

  useEffect(() => {
    api.get<{ competitions: Competition[]; total: number }>('competitions')
      .then(({ data }) => setCompetitions(data.competitions || data as unknown as Competition[]))
      .catch(() => {});
  }, []);

  const fetchRooms = async (compId: string) => {
    if (!compId) return;
    setLoading(true);
    try {
      const { data } = await api.get<{ rooms: Room[] }>(`rooms/${compId}`);
      setRooms(data.rooms);
    } catch {
      setError('Не удалось загрузить аудитории');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (selectedCompetition) {
      fetchRooms(selectedCompetition);
    }
  }, [selectedCompetition]);

  const handleCreate = async () => {
    if (!selectedCompetition) return;
    setCreating(true);
    setError(null);
    try {
      await api.post(`rooms/${selectedCompetition}`, {
        name: formName,
        capacity: parseInt(formCapacity),
      });
      setFormName('');
      setFormCapacity('');
      await fetchRooms(selectedCompetition);
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Ошибка';
      setError(msg);
    } finally {
      setCreating(false);
    }
  };

  const handleDelete = async (roomId: string) => {
    if (!confirm('Удалить аудиторию?')) return;
    try {
      await api.delete(`rooms/room/${roomId}`);
      if (selectedCompetition) await fetchRooms(selectedCompetition);
    } catch {
      setError('Не удалось удалить');
    }
  };

  return (
    <Layout>
      <h1 className="mb-24">Аудитории</h1>

      {error && <div className="alert alert-error mb-16">{error}</div>}

      <div className="mb-16">
        <label>Олимпиада</label>
        <select
          className="input"
          value={selectedCompetition}
          onChange={(e) => setSelectedCompetition(e.target.value)}
          style={{ width: '100%' }}
        >
          <option value="">Выберите олимпиаду...</option>
          {competitions.map((c) => (
            <option key={c.id} value={c.id}>{c.name}</option>
          ))}
        </select>
      </div>

      {selectedCompetition && (
        <>
          <div className="card mb-16">
            <h3 className="mb-16">Добавить аудиторию</h3>
            <div className="flex gap-8" style={{ alignItems: 'flex-end' }}>
              <div>
                <label>Название</label>
                <input className="input" value={formName} onChange={(e) => setFormName(e.target.value)} placeholder="Ауд. 301" />
              </div>
              <div>
                <label>Вместимость</label>
                <input className="input" type="number" value={formCapacity} onChange={(e) => setFormCapacity(e.target.value)} placeholder="30" />
              </div>
              <Button onClick={handleCreate} loading={creating}>Добавить</Button>
            </div>
          </div>

          {loading ? (
            <p>Загрузка...</p>
          ) : (
            <table className="table">
              <thead>
                <tr>
                  <th>Название</th>
                  <th>Вместимость</th>
                  <th>Действия</th>
                </tr>
              </thead>
              <tbody>
                {rooms.map((room) => (
                  <tr key={room.id}>
                    <td>{room.name}</td>
                    <td>{room.capacity}</td>
                    <td>
                      <Button variant="secondary" onClick={() => handleDelete(room.id)}>
                        Удалить
                      </Button>
                    </td>
                  </tr>
                ))}
                {rooms.length === 0 && (
                  <tr>
                    <td colSpan={3} style={{ textAlign: 'center' }}>Нет аудиторий</td>
                  </tr>
                )}
              </tbody>
            </table>
          )}
        </>
      )}
    </Layout>
  );
};

export default RoomsPage;
