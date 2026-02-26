"use client";
import React, { useState, useCallback, useMemo } from 'react';
import { useDropzone } from 'react-dropzone';
import axios from 'axios';
import {
    useReactTable,
    getCoreRowModel,
    flexRender,
} from '@tanstack/react-table';
import { useVirtualizer } from '@tanstack/react-virtual';
import { CloudUpload, AlertCircle, CheckCircle2, Save, Trash2 } from 'lucide-react';

const API_BASE = 'http://localhost:5001/api';

export default function LotePage() {
    const [data, setData] = useState([]);
    const [errors, setErrors] = useState([]);
    const [loading, setLoading] = useState(false);
    const [fileName, setFileName] = useState("");

    const onDrop = useCallback(async (acceptedFiles) => {
        const file = acceptedFiles[0];
        if (!file) return;

        setFileName(file.name);
        setLoading(true);
        const formData = new FormData();
        formData.append('file', file);

        try {
            const resp = await axios.post(`${API_BASE}/lote/validar`, formData);
            if (resp.data.success) {
                setData(resp.data.data);
                setErrors(resp.data.errors);
            }
        } catch (err) {
            console.error("Erro no upload:", err);
            alert("Falha ao processar arquivo.");
        } finally {
            setLoading(false);
        }
    }, []);

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        accept: {
            'text/csv': ['.csv'],
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
            'application/vnd.ms-excel': ['.xls']
        },
        multiple: false
    });

    // Configuração da Tabela
    const columns = useMemo(() => {
        if (data.length === 0) return [];
        return Object.keys(data[0]).map(key => ({
            accessorKey: key,
            header: key.toUpperCase(),
            size: 150,
        }));
    }, [data]);

    const table = useReactTable({
        data,
        columns,
        getCoreRowModel: getCoreRowModel(),
    });

    const { rows } = table.getRowModel();

    // Virtualização para 6k+ registros
    const parentRef = React.useRef(null);
    const virtualizer = useVirtualizer({
        count: rows.length,
        getScrollElement: () => parentRef.current,
        estimateSize: () => 45,
        overscan: 10,
    });

    const items = virtualizer.getVirtualItems();

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <div>
                    <h2 className="text-2xl font-bold">Importação em Lote</h2>
                    <p className="text-gray-500 text-sm">Upload massivo de fonogramas para validação e cadastro</p>
                </div>
                {data.length > 0 && (
                    <div className="flex gap-3">
                        <button
                            onClick={() => { setData([]); setErrors([]); setFileName(""); }}
                            className="px-4 py-2 border border-gray-200 rounded-lg text-sm font-medium hover:bg-gray-50 transition-all flex items-center gap-2"
                        >
                            <Trash2 size={16} /> Limpar
                        </button>
                        <button
                            className="px-6 py-2 bg-navy-primary text-white rounded-lg text-sm font-bold shadow-lg hover:bg-navy-secondary transition-all flex items-center gap-2"
                        >
                            <Save size={16} /> Confirmar Cadastro
                        </button>
                    </div>
                )}
            </div>

            {/* Dropzone */}
            {data.length === 0 && (
                <div
                    {...getRootProps()}
                    className={`border-2 border-dashed rounded-2xl p-16 flex flex-col items-center justify-center transition-all cursor-pointer ${isDragActive ? 'border-accent-red bg-accent-red/5' : 'border-gray-200 hover:border-navy-primary hover:bg-gray-50'
                        }`}
                >
                    <input {...getInputProps()} />
                    <div className="w-16 h-16 bg-navy-primary/10 rounded-full flex items-center justify-center text-navy-primary mb-4">
                        <CloudUpload size={32} />
                    </div>
                    <h3 className="text-lg font-semibold">Arraste sua planilha aqui</h3>
                    <p className="text-gray-400 text-sm mt-1">Suporta CSV, XLSX e XLS (Recomendado: até 10.000 linhas)</p>
                </div>
            )}

            {/* Resultados / Grid */}
            {data.length > 0 && (
                <div className="bg-white border border-black/10 rounded-2xl overflow-hidden shadow-sm">
                    <div className="p-4 bg-gray-50 border-b border-black/10 flex justify-between items-center">
                        <div className="flex gap-6">
                            <div className="flex items-center gap-2">
                                <span className="w-2 h-2 rounded-full bg-navy-primary"></span>
                                <span className="text-xs font-bold uppercase text-gray-500 tracking-wider">Total: {data.length}</span>
                            </div>
                            <div className="flex items-center gap-2">
                                <span className="w-2 h-2 rounded-full bg-accent-red"></span>
                                <span className="text-xs font-bold uppercase text-gray-500 tracking-wider">Erros: {errors.length}</span>
                            </div>
                        </div>
                        <span className="text-xs text-gray-400">{fileName}</span>
                    </div>

                    {/* Tabela Virtualizada */}
                    <div
                        ref={parentRef}
                        className="overflow-auto max-h-[600px] relative"
                    >
                        <table className="w-full text-left border-collapse table-fixed">
                            <thead className="sticky top-0 z-10 bg-white shadow-sm">
                                {table.getHeaderGroups().map(headerGroup => (
                                    <tr key={headerGroup.id}>
                                        {headerGroup.headers.map(header => (
                                            <th
                                                key={header.id}
                                                className="p-3 text-[10px] font-bold text-gray-400 border-b border-gray-100 uppercase tracking-widest bg-gray-50/50"
                                                style={{ width: header.getSize() }}
                                            >
                                                {flexRender(header.column.columnDef.header, header.getContext())}
                                            </th>
                                        ))}
                                    </tr>
                                ))}
                            </thead>
                            <tbody
                                style={{ height: `${virtualizer.getTotalSize()}px` }}
                                className="relative"
                            >
                                {items.map(virtualRow => {
                                    const row = rows[virtualRow.index];
                                    // Simulação de erro visual (ex: se título estiver vazio ou ISRC inválido)
                                    const hasError = errors.some(e => e.linha === virtualRow.index + 1);

                                    return (
                                        <tr
                                            key={virtualRow.key}
                                            data-index={virtualRow.index}
                                            ref={virtualizer.measureElement}
                                            className={`absolute top-0 left-0 w-full flex items-center border-b border-gray-50 hover:bg-gray-50/50 transition-colors ${hasError ? 'bg-red-50/50 border-l-4 border-l-accent-red' : ''
                                                }`}
                                            style={{ transform: `translateY(${virtualRow.start}px)` }}
                                        >
                                            {row.getVisibleCells().map(cell => (
                                                <td
                                                    key={cell.id}
                                                    className="p-3 text-xs text-gray-600 truncate whitespace-nowrap overflow-hidden"
                                                    style={{ width: cell.column.getSize() }}
                                                >
                                                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                                                </td>
                                            ))}
                                        </tr>
                                    );
                                })}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}
        </div>
    );
}
