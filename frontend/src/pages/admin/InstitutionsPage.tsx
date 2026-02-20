import React, { useState, useEffect } from 'react';
import api from '../../api/client';
import Layout from '../../components/layout/Layout';
import Button from '../../components/common/Button';
import type { Institution } from '../../types';

const InstitutionsPage: React.FC = () => {
  const [institutions, setInstitutions] = useState<Institution[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showModal, setShowModal] = useState(false);
  const [formName, setFormName] = useState('');
  const [formShortName, setFormShortName] = useState('');
  const [formCity, setFormCity] = useState('');
  const [creating, setCreating] = useState(false);

  const fetchInstitutions = async () => {
    setLoading(true);
    try {
      const { data } = await api.get<{ institutions: Institution[]; total: number }>('institutions');
      setInstitutions(data.institutions);
    } catch {
      setError('Не удалось загрузить учреждения');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchInstitutions();
  }, []);

  const handleCreate = async () => {
    setCreating(true);
    setError(null);
    try {
      await api.post('institutions', {
        name: formName,
        short_name: formShortName || null,
        city: formCity || null,
      });
      setShowModal(false);
      setFormName('');
      setFormShortName('');
      setFormCity('');
      await fetchInstitutions();
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Ошибка';
      setError(msg);
    } finally {
      setCreating(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Удалить учреждение?')) return;
    try {
      await api.delete(`institutions/${id}`);
      await fetchInstitutions();
    } catch {
      setError('Не удалось удалить');
    }
  };

  return (
    <Layout>
      <h1 className="mb-24">Учреждения</h1>

      {error && <div className="alert alert-error mb-16">{error}</div>}

      <div className="mb-16">
        <Button onClick={() => setShowModal(true)}>Добавить учреждение</Button>
      </div>

      {loading ? (
        <p>Загрузка...</p>
      ) : (
        <table className="table">
          <thead>
            <tr>
              <th>Название</th>
              <th>Сокращение</th>
              <th>Город</th>
              <th>Действия</th>
            </tr>
          </thead>
          <tbody>
            {institutions.map((inst) => (
              <tr key={inst.id}>
                <td>{inst.name}</td>
                <td>{inst.short_name || '—'}</td>
                <td>{inst.city || '—'}</td>
                <td>
                  <Button variant="secondary" onClick={() => handleDelete(inst.id)}>
                    Удалить
                  </Button>
                </td>
              </tr>
            ))}
            {institutions.length === 0 && (
              <tr>
                <td colSpan={4} style={{ textAlign: 'center' }}>Нет учреждений</td>
              </tr>
            )}
          </tbody>
        </table>
      )}

      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="card" onClick={(e) => e.stopPropagation()} style={{ maxWidth: 500, margin: '100px auto' }}>
            <h2 className="mb-16">Новое учреждение</h2>
            <div className="mb-16">
              <label>Название *</label>
              <input className="input" value={formName} onChange={(e) => setFormName(e.target.value)} style={{ width: '100%' }} />
            </div>
            <div className="mb-16">
              <label>Сокращение</label>
              <input className="input" value={formShortName} onChange={(e) => setFormShortName(e.target.value)} style={{ width: '100%' }} />
            </div>
            <div className="mb-16">
              <label>Город</label>
              <input className="input" value={formCity} onChange={(e) => setFormCity(e.target.value)} style={{ width: '100%' }} />
            </div>
            <div className="flex gap-8">
              <Button onClick={handleCreate} loading={creating}>Создать</Button>
              <Button variant="secondary" onClick={() => setShowModal(false)}>Отмена</Button>
            </div>
          </div>
        </div>
      )}
    </Layout>
  );
};

export default InstitutionsPage;
