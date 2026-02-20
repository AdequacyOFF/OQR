import React, { useState, useEffect, useRef } from 'react';
import api from '../../api/client';
import type { Institution } from '../../types';

interface Props {
  value: string;
  onChange: (value: string, institutionId?: string) => void;
  placeholder?: string;
}

const InstitutionAutocomplete: React.FC<Props> = ({ value, onChange, placeholder = 'Начните вводить...' }) => {
  const [suggestions, setSuggestions] = useState<Institution[]>([]);
  const [showDropdown, setShowDropdown] = useState(false);
  const [loading, setLoading] = useState(false);
  const timeoutRef = useRef<number | null>(null);
  const wrapperRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (wrapperRef.current && !wrapperRef.current.contains(e.target as Node)) {
        setShowDropdown(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = e.target.value;
    onChange(val);

    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }

    if (val.length < 2) {
      setSuggestions([]);
      setShowDropdown(false);
      return;
    }

    timeoutRef.current = window.setTimeout(async () => {
      setLoading(true);
      try {
        const { data } = await api.get<Institution[]>(`institutions/search?q=${encodeURIComponent(val)}&limit=10`);
        setSuggestions(data);
        setShowDropdown(data.length > 0);
      } catch {
        setSuggestions([]);
      } finally {
        setLoading(false);
      }
    }, 300);
  };

  const handleSelect = (inst: Institution) => {
    onChange(inst.name, inst.id);
    setShowDropdown(false);
    setSuggestions([]);
  };

  return (
    <div ref={wrapperRef} style={{ position: 'relative' }}>
      <input
        type="text"
        className="input"
        value={value}
        onChange={handleInputChange}
        onFocus={() => suggestions.length > 0 && setShowDropdown(true)}
        placeholder={placeholder}
        style={{ width: '100%' }}
      />
      {loading && (
        <div style={{ position: 'absolute', right: '12px', top: '50%', transform: 'translateY(-50%)', fontSize: '12px', color: '#a0aec0' }}>
          ...
        </div>
      )}
      {showDropdown && suggestions.length > 0 && (
        <div style={{
          position: 'absolute',
          top: '100%',
          left: 0,
          right: 0,
          background: 'white',
          border: '1px solid #e2e8f0',
          borderRadius: '0 0 8px 8px',
          boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
          zIndex: 100,
          maxHeight: '200px',
          overflowY: 'auto',
        }}>
          {suggestions.map((inst) => (
            <div
              key={inst.id}
              onClick={() => handleSelect(inst)}
              style={{
                padding: '10px 12px',
                cursor: 'pointer',
                borderBottom: '1px solid #f7fafc',
              }}
              onMouseEnter={(e) => (e.currentTarget.style.background = '#ebf8ff')}
              onMouseLeave={(e) => (e.currentTarget.style.background = 'white')}
            >
              <div style={{ fontWeight: 500 }}>{inst.name}</div>
              {inst.city && <div style={{ fontSize: '12px', color: '#a0aec0' }}>{inst.city}</div>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default InstitutionAutocomplete;
