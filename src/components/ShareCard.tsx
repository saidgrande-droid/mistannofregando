/**
 * src/components/ShareCard.tsx
 * Ultra-Fast Zero-Dependency HTML5 2D Canvas Share Card Generator (1080x1080px Retina)
 * and Multi-Channel Social Sharing Pipeline for "Mi Stanno Fregando?".
 */

import React, { useEffect, useRef, useState, useCallback, useMemo } from 'react';
import { Share2, Download, Copy, Check } from 'lucide-react';
import { CalculationResult, CategoryId } from '../core/types';

// ==========================================
// 1. Types & Interfaces
// ==========================================

export interface ShareCardRenderParams {
  calculationResult: CalculationResult;
  categoryId: CategoryId;
  categoryName: string;
  prestationName: string;
  provinceName: string;
  provinceSigla: string;
}

export interface ShareCardProps {
  /** Mathematical result from src/core/calculator.ts */
  calculationResult: CalculationResult;
  /** Active Category ID (e.g. 'auto', 'dentista') */
  categoryId: CategoryId;
  /** Prestation ID slug (e.g. 'auto_tagliando', 'dentista_impianto') */
  prestationId: string;
  /** Province 2-letter uppercase sigla (e.g. 'MI', 'RM', 'NA') */
  provinceSigla: string;
  /** Optional display name for category */
  categoryName?: string;
  /** Optional display name for prestation */
  prestationName?: string;
  /** Optional display name for province */
  provinceName?: string;
  /** Optional custom prestation description */
  customDescription?: string;
  /** Optional callback fired when any share action is completed */
  onShareComplete?: (channel: 'whatsapp' | 'webshare' | 'download' | 'copylink') => void;
  /** Optional container class overrides */
  className?: string;
}

// ==========================================
// 2. Pure Canvas 2D Drawing Utilities
// ==========================================

function drawRoundRect(
  ctx: CanvasRenderingContext2D,
  x: number,
  y: number,
  w: number,
  h: number,
  r: number
): void {
  if (typeof ctx.roundRect === 'function') {
    ctx.beginPath();
    ctx.roundRect(x, y, w, h, r);
  } else {
    ctx.beginPath();
    ctx.moveTo(x + r, y);
    ctx.lineTo(x + w - r, y);
    ctx.quadraticCurveTo(x + w, y, x + w, y + r);
    ctx.lineTo(x + w, y + h - r);
    ctx.quadraticCurveTo(x + w, y + h, x + w - r, y + h);
    ctx.lineTo(x + r, y + h);
    ctx.quadraticCurveTo(x, y + h, x, y + h - r);
    ctx.lineTo(x, y + r);
    ctx.quadraticCurveTo(x, y, x + r, y);
    ctx.closePath();
  }
}

export function wrapCanvasText(
  ctx: CanvasRenderingContext2D,
  text: string,
  maxWidth: number
): string[] {
  if (!text) return [];
  const words = text.split(' ');
  const lines: string[] = [];
  let currentLine = words[0] || '';

  for (let i = 1; i < words.length; i++) {
    const word = words[i];
    const testLine = `${currentLine} ${word}`;
    const metrics = ctx.measureText(testLine);
    if (metrics.width > maxWidth) {
      lines.push(currentLine);
      currentLine = word;
    } else {
      currentLine = testLine;
    }
  }
  if (currentLine) {
    lines.push(currentLine);
  }
  return lines;
}

/**
 * Synchronous/microtask Canvas 2D render engine.
 * Renders a high-contrast, Neo-Pop 1080x1080px viral card with zero overlapping colors.
 */
export function renderShareCardToCanvas(
  canvas: HTMLCanvasElement,
  params: ShareCardRenderParams
): void {
  const ctx = canvas.getContext('2d');
  if (!ctx) return;

  const {
    calculationResult,
    categoryName,
    prestationName,
    provinceName,
    provinceSigla,
  } = params;

  const {
    quote,
    refPrice,
    diffEuro,
    diffPct,
    zone,
    isAlert,
    needleAngle,
    headline,
  } = calculationResult;

  // Set physical dimensions
  canvas.width = 1080;
  canvas.height = 1080;

  // ----------------------------------------------------
  // Layer 1: High-Contrast Neo-Pop Background & Frame
  // ----------------------------------------------------
  const baseGrad = ctx.createLinearGradient(0, 0, 1080, 1080);
  baseGrad.addColorStop(0, '#FFFBEB');
  baseGrad.addColorStop(0.5, '#FFFFFF');
  baseGrad.addColorStop(1, '#FFF1F2');
  ctx.fillStyle = baseGrad;
  ctx.fillRect(0, 0, 1080, 1080);

  // Outer Bold Neo-Brutalist Card Frame
  drawRoundRect(ctx, 24, 24, 1032, 1032, 32);
  ctx.fillStyle = '#FFFFFF';
  ctx.fill();
  ctx.strokeStyle = '#0F172A';
  ctx.lineWidth = 8;
  ctx.stroke();

  // Radial Ambient Backglow matching verdict
  const radialGlow = ctx.createRadialGradient(540, 430, 40, 540, 430, 380);
  if (zone === 'TI_STANNO_FREGANDO') {
    radialGlow.addColorStop(0, 'rgba(239, 68, 68, 0.14)');
    radialGlow.addColorStop(1, 'rgba(239, 68, 68, 0)');
  } else if (zone === 'PREZZO_ONESTO') {
    radialGlow.addColorStop(0, 'rgba(16, 185, 129, 0.14)');
    radialGlow.addColorStop(1, 'rgba(16, 185, 129, 0)');
  } else {
    radialGlow.addColorStop(0, 'rgba(245, 158, 11, 0.14)');
    radialGlow.addColorStop(1, 'rgba(245, 158, 11, 0)');
  }
  ctx.fillStyle = radialGlow;
  ctx.fillRect(30, 30, 1020, 1020);

  // ----------------------------------------------------
  // Layer 2: Branded Header Pill (Dark Background, Crisp White Text)
  // ----------------------------------------------------
  drawRoundRect(ctx, 300, 58, 480, 54, 27);
  ctx.fillStyle = '#0F172A';
  ctx.fill();

  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.font = '900 22px system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
  ctx.fillStyle = '#FBBF24';
  ctx.fillText('MISTANNOFREGANDO.IT', 540, 85);

  // ----------------------------------------------------
  // Layer 3: Category & Prestation Header (Dark Ink on White)
  // ----------------------------------------------------
  ctx.font = '800 20px system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
  ctx.fillStyle = '#E11D48';
  ctx.fillText(categoryName.toUpperCase(), 540, 145);

  const serviceTitle = `${prestationName} a ${provinceName || provinceSigla}`;
  ctx.font = '900 38px system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
  ctx.fillStyle = '#0F172A';

  let displayTitle = serviceTitle;
  if (ctx.measureText(displayTitle).width > 880) {
    while (ctx.measureText(`${displayTitle}...`).width > 880 && displayTitle.length > 0) {
      displayTitle = displayTitle.slice(0, -1);
    }
    displayTitle = `${displayTitle}...`;
  }
  ctx.fillText(displayTitle, 540, 192);

  // ----------------------------------------------------
  // Layer 4: Speedometer Gauge Graphic (200° Arc)
  // Center: (540, 430), R: 160, Width: 26
  // ----------------------------------------------------
  const cx = 540;
  const cy = 430;
  const radius = 160;
  const arcWidth = 26;

  const toRad = (deg: number) => (deg * Math.PI) / 180;

  // Soft Inner Dial Circle
  ctx.beginPath();
  ctx.arc(cx, cy, 128, 0, Math.PI * 2);
  ctx.fillStyle = '#F8FAFC';
  ctx.fill();

  // Background Full Arc Track (Dark border for crisp contrast)
  ctx.beginPath();
  ctx.arc(cx, cy, radius, toRad(170), toRad(370), false);
  ctx.strokeStyle = '#0F172A';
  ctx.lineWidth = arcWidth + 10;
  ctx.lineCap = 'round';
  ctx.stroke();

  // Outer End Caps at 170° and 370° (10°) so inner color joins are 100% flat!
  const startX = cx + radius * Math.cos(toRad(170));
  const startY = cy + radius * Math.sin(toRad(170));
  ctx.beginPath();
  ctx.arc(startX, startY, arcWidth / 2, 0, Math.PI * 2);
  ctx.fillStyle = '#10B981';
  ctx.fill();

  const endX = cx + radius * Math.cos(toRad(10));
  const endY = cy + radius * Math.sin(toRad(10));
  ctx.beginPath();
  ctx.arc(endX, endY, arcWidth / 2, 0, Math.PI * 2);
  ctx.fillStyle = '#EF4444';
  ctx.fill();

  // Zone 1: Green (170° to 270°, 100° span) — flat butt join
  ctx.beginPath();
  ctx.arc(cx, cy, radius, toRad(170), toRad(270), false);
  ctx.strokeStyle = '#10B981';
  ctx.lineWidth = arcWidth;
  ctx.lineCap = 'butt';
  ctx.stroke();

  // Zone 2: Amber (270° to 320°, 50° span) — flat butt join
  ctx.beginPath();
  ctx.arc(cx, cy, radius, toRad(270), toRad(320), false);
  ctx.strokeStyle = '#F59E0B';
  ctx.lineWidth = arcWidth;
  ctx.lineCap = 'butt';
  ctx.stroke();

  // Zone 3: Red (320° to 370°, 50° span) — flat butt join (no round bump into yellow!)
  ctx.beginPath();
  ctx.arc(cx, cy, radius, toRad(320), toRad(370), false);
  ctx.strokeStyle = '#EF4444';
  ctx.lineWidth = arcWidth;
  ctx.lineCap = 'butt';
  ctx.stroke();

  // Non-overlapping High-Contrast Zone Labels (Placed cleanly outside the arc)
  ctx.font = '900 18px system-ui, -apple-system, sans-serif';
  ctx.fillStyle = '#047857';
  ctx.fillText('ONESTO', 360, 504);

  ctx.fillStyle = '#B45309';
  ctx.fillText('MEDIA (0%)', 540, 240);

  ctx.fillStyle = '#B91C1C';
  ctx.fillText('FUORI MERCATO', 720, 504);

  // Dynamic Needle (Dark #0F172A needle on light dial so it's 100% visible)
  const needleDeg = -90 + (needleAngle || 0);
  const needleRad = toRad(needleDeg);
  const needleLength = 132;

  ctx.save();
  ctx.translate(cx, cy);
  ctx.rotate(needleRad);

  ctx.shadowColor = 'rgba(15, 23, 42, 0.25)';
  ctx.shadowBlur = 8;
  ctx.fillStyle = '#0F172A';

  ctx.beginPath();
  ctx.moveTo(0, -7);
  ctx.lineTo(needleLength, 0);
  ctx.lineTo(0, 7);
  ctx.lineTo(-16, 0);
  ctx.closePath();
  ctx.fill();

  ctx.restore();

  // Needle Hub Cap
  ctx.beginPath();
  ctx.arc(cx, cy, 18, 0, Math.PI * 2);
  ctx.fillStyle = '#0F172A';
  ctx.fill();

  ctx.beginPath();
  ctx.arc(cx, cy, 8, 0, Math.PI * 2);
  ctx.fillStyle = '#FBBF24';
  ctx.fill();

  // ----------------------------------------------------
  // Layer 5: Giant Verdict Stamp / Badge (High Contrast)
  // ----------------------------------------------------
  const badgeY = 540;
  const badgeH = 92;
  drawRoundRect(ctx, 110, badgeY, 860, badgeH, 24);

  let verdictBg = '#059669';
  let verdictText = '';

  if (zone === 'TI_STANNO_FREGANDO') {
    verdictBg = isAlert ? '#DC2626' : '#E11D48';
    verdictText = isAlert
      ? `TI STANNO FREGANDO! (+${diffPct.toFixed(1)}%)`
      : `FUORI MERCATO (+${diffPct.toFixed(1)}%)`;
  } else if (zone === 'NELLA_MEDIA') {
    verdictBg = '#D97706';
    const sign = diffPct >= 0 ? '+' : '';
    verdictText = `PREZZO NELLA MEDIA (${sign}${diffPct.toFixed(1)}%)`;
  } else {
    verdictBg = '#059669';
    verdictText = `PREZZO ONESTO (${diffPct.toFixed(1)}%)`;
  }

  ctx.fillStyle = verdictBg;
  ctx.fill();
  ctx.strokeStyle = '#0F172A';
  ctx.lineWidth = 5;
  ctx.stroke();

  ctx.font = '900 35px system-ui, -apple-system, sans-serif';
  ctx.fillStyle = '#FFFFFF';
  ctx.fillText(verdictText, 540, badgeY + badgeH / 2);

  // ----------------------------------------------------
  // Layer 6: Highlighted Quote vs Benchmark Comparison Box
  // ----------------------------------------------------
  const boxY = 662;
  const boxH = 140;
  drawRoundRect(ctx, 90, boxY, 900, boxH, 24);
  ctx.fillStyle = '#F8FAFC';
  ctx.fill();
  ctx.strokeStyle = '#0F172A';
  ctx.lineWidth = 4;
  ctx.stroke();

  // Left Column: Quote
  ctx.font = '800 17px system-ui, -apple-system, sans-serif';
  ctx.fillStyle = '#475569';
  ctx.fillText('PREVENTIVO RICEVUTO', 315, boxY + 38);

  ctx.font = '900 44px system-ui, -apple-system, sans-serif';
  ctx.fillStyle = '#0F172A';
  ctx.fillText(`${quote.toLocaleString('it-IT')} €`, 315, boxY + 92);

  // Vertical Divider
  ctx.beginPath();
  ctx.moveTo(540, boxY + 22);
  ctx.lineTo(540, boxY + 118);
  ctx.strokeStyle = '#CBD5E1';
  ctx.lineWidth = 3;
  ctx.stroke();

  // Right Column: Local Ref
  ctx.font = '800 17px system-ui, -apple-system, sans-serif';
  ctx.fillStyle = '#475569';
  ctx.fillText(`MEDIA LOCALE (${provinceSigla.toUpperCase()})`, 765, boxY + 38);

  ctx.font = '900 44px system-ui, -apple-system, sans-serif';
  ctx.fillStyle = '#0284C7';
  ctx.fillText(`${refPrice.toLocaleString('it-IT')} €`, 765, boxY + 92);

  // Delta Sub-Badge
  const deltaText =
    diffEuro > 0
      ? `Differenza: +${diffEuro.toLocaleString('it-IT')} € (+${diffPct.toFixed(1)}% sopra la media)`
      : diffEuro < 0
      ? `Risparmio: ${Math.abs(diffEuro).toLocaleString('it-IT')} € (${diffPct.toFixed(1)}%)`
      : 'In perfetta parità con la media locale (0.0%)';

  ctx.font = '800 20px system-ui, -apple-system, sans-serif';
  ctx.fillStyle = diffEuro > 0 ? '#DC2626' : '#059669';
  ctx.fillText(deltaText, 540, 836);

  // ----------------------------------------------------
  // Layer 7: Emotional Headline / Punchline
  // ----------------------------------------------------
  ctx.font = 'italic 800 23px system-ui, -apple-system, sans-serif';
  ctx.fillStyle = '#1E293B';

  const headlineLines = wrapCanvasText(ctx, `«${headline}»`, 860);
  const headlineStartY = 880;
  headlineLines.slice(0, 2).forEach((line, idx) => {
    ctx.fillText(line, 540, headlineStartY + idx * 30);
  });

  // ----------------------------------------------------
  // Layer 8: Watermark & Viral CTA Footer
  // ----------------------------------------------------
  drawRoundRect(ctx, 90, 956, 900, 64, 18);
  ctx.fillStyle = '#0F172A';
  ctx.fill();

  ctx.font = '900 22px system-ui, -apple-system, sans-serif';
  ctx.fillStyle = '#FFFFFF';
  ctx.fillText('Confronta gratis il tuo preventivo su mistannofregando.it', 540, 988);
}

// ==========================================
// 3. Sharing URL & Text Formatters
// ==========================================

export function generateViralShareText(params: {
  prestationName: string;
  provinceName: string;
  quote: number;
  refPrice: number;
  diffEuro: number;
  diffPct: number;
  zone: string;
  headline?: string;
  shareUrl: string;
}): string {
  const diffSign = params.diffPct >= 0 ? '+' : '';
  const euroSign = params.diffEuro >= 0 ? '+' : '';
  const formattedQuote = `${params.quote.toLocaleString('it-IT')} €`;
  const formattedRef = `${params.refPrice.toLocaleString('it-IT')} €`;
  const formattedDiffEuro = `${euroSign}${params.diffEuro.toLocaleString('it-IT')} €`;

  const leadLine =
    params.zone === 'TI_STANNO_FREGANDO'
      ? '🚨 TI STANNO FREGANDO?'
      : params.zone === 'PREZZO_ONESTO'
      ? '✅ PREZZO ONESTO!'
      : '⚖️ PREZZO NELLA MEDIA';

  return `${leadLine}
Ho controllato il preventivo per ${params.prestationName} a ${params.provinceName} su MiStannoFregando.it: verdetto ${params.zone} (${diffSign}${params.diffPct}%)!

• Preventivo ricevuto: ${formattedQuote}
• Media locale: ${formattedRef}
• Differenza: ${formattedDiffEuro} (${diffSign}${params.diffPct}%)

${params.headline ? `«${params.headline}»\n\n` : ''}🔍 Controlla gratis il tuo preventivo prima di pagare:
${params.shareUrl}`;
}

export function buildShareUrl(
  baseUrl: string,
  categoryId: CategoryId,
  prestationId: string,
  provinceSigla: string,
  quote: number,
  customDescription?: string
): string {
  const cleanBase = baseUrl.split('?')[0].replace(/\/+$/, '');
  const params = new URLSearchParams({
    cat: categoryId,
    prest: prestationId,
    prov: provinceSigla.toUpperCase(),
    quote: String(quote),
  });
  if (prestationId === 'custom' && customDescription && customDescription.trim()) {
    params.set('desc', customDescription.trim());
  }
  return `${cleanBase}/?${params.toString()}`;
}

export function parseShareUrlParams(queryString: string): Partial<{
  categoryId: CategoryId;
  prestationId: string;
  provinceSigla: string;
  quote: number;
  customDescription: string;
}> {
  const search = queryString.startsWith('?') ? queryString.slice(1) : queryString;
  const params = new URLSearchParams(search);
  const result: Partial<{
    categoryId: CategoryId;
    prestationId: string;
    provinceSigla: string;
    quote: number;
    customDescription: string;
  }> = {};

  const cat = params.get('cat');
  if (cat) result.categoryId = cat as CategoryId;

  const prest = params.get('prest');
  if (prest) result.prestationId = prest;

  const prov = params.get('prov');
  if (prov) result.provinceSigla = prov.toUpperCase();

  const desc = params.get('desc');
  if (desc) result.customDescription = desc;

  const quoteStr = params.get('quote');
  if (quoteStr) {
    const parsedQuote = parseFloat(quoteStr);
    if (Number.isFinite(parsedQuote) && parsedQuote >= 0) {
      result.quote = parsedQuote;
    }
  }

  return result;
}

// ==========================================
// 4. React ShareCard Component
// ==========================================

export const ShareCard: React.FC<ShareCardProps> = ({
  calculationResult,
  categoryId,
  prestationId,
  provinceSigla,
  categoryName = 'Servizio',
  prestationName = 'Intervento',
  provinceName = 'Italia',
  customDescription,
  onShareComplete,
  className = '',
}) => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const [copied, setCopied] = useState(false);
  const [canNativeShare, setCanNativeShare] = useState(false);

  const shareBaseUrl = useMemo(() => {
    if (typeof window !== 'undefined' && window.location) {
      return `${window.location.origin}${window.location.pathname}`;
    }
    return 'https://mistannofregando.it';
  }, []);

  const shareUrl = useMemo(
    () =>
      buildShareUrl(
        shareBaseUrl,
        categoryId,
        prestationId,
        provinceSigla,
        calculationResult.quote,
        customDescription
      ),
    [shareBaseUrl, categoryId, prestationId, provinceSigla, calculationResult.quote, customDescription]
  );

  const shareText = useMemo(
    () =>
      generateViralShareText({
        prestationName,
        provinceName,
        quote: calculationResult.quote,
        refPrice: calculationResult.refPrice,
        diffEuro: calculationResult.diffEuro,
        diffPct: calculationResult.diffPct,
        zone: calculationResult.zone,
        headline: calculationResult.headline,
        shareUrl,
      }),
    [prestationName, provinceName, calculationResult, shareUrl]
  );

  const whatsAppUrl = useMemo(
    () => `https://api.whatsapp.com/send?text=${encodeURIComponent(shareText)}`,
    [shareText]
  );

  useEffect(() => {
    if (typeof navigator !== 'undefined' && typeof navigator.share === 'function') {
      setCanNativeShare(true);
    }
  }, []);

  useEffect(() => {
    if (canvasRef.current) {
      renderShareCardToCanvas(canvasRef.current, {
        calculationResult,
        categoryId,
        categoryName,
        prestationName,
        provinceName,
        provinceSigla,
      });
    }
  }, [
    calculationResult,
    categoryId,
    categoryName,
    prestationName,
    provinceName,
    provinceSigla,
  ]);

  const handleWhatsAppShare = useCallback(() => {
    onShareComplete?.('whatsapp');
  }, [onShareComplete]);

  const handleDirectDownload = useCallback(() => {
    if (!canvasRef.current) return;
    try {
      if (canvasRef.current.toBlob) {
        canvasRef.current.toBlob((blob) => {
          if (!blob) return;
          const url = URL.createObjectURL(blob);
          const link = document.createElement('a');
          link.href = url;
          link.download = `mi-stanno-fregando-${prestationId}-${provinceSigla}.png`;
          document.body.appendChild(link);
          link.click();
          document.body.removeChild(link);
          URL.revokeObjectURL(url);
          onShareComplete?.('download');
        }, 'image/png');
      } else {
        const dataUrl = canvasRef.current.toDataURL('image/png');
        const link = document.createElement('a');
        link.href = dataUrl;
        link.download = `mi-stanno-fregando-${prestationId}-${provinceSigla}.png`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        onShareComplete?.('download');
      }
    } catch {
      // Ignore download errors in non-browser envs
    }
  }, [prestationId, provinceSigla, onShareComplete]);

  const handleWebShare = useCallback(async () => {
    if (!canvasRef.current) return;

    if (typeof navigator !== 'undefined' && navigator.share) {
      try {
        if (canvasRef.current.toBlob && typeof File !== 'undefined') {
          canvasRef.current.toBlob(async (blob) => {
            if (blob) {
              const file = new File([blob], 'scheda-verdetto.png', { type: 'image/png' });
              if (navigator.canShare && navigator.canShare({ files: [file] })) {
                await navigator.share({
                  title: 'Mi Stanno Fregando?',
                  text: shareText,
                  files: [file],
                });
                onShareComplete?.('webshare');
                return;
              }
            }
            await navigator.share({
              title: 'Mi Stanno Fregando?',
              text: shareText,
              url: shareUrl,
            });
            onShareComplete?.('webshare');
          }, 'image/png');
        } else {
          await navigator.share({
            title: 'Mi Stanno Fregando?',
            text: shareText,
            url: shareUrl,
          });
          onShareComplete?.('webshare');
        }
      } catch (err: unknown) {
        if (err instanceof Error && err.name !== 'AbortError') {
          handleDirectDownload();
        }
      }
    } else {
      handleDirectDownload();
    }
  }, [shareText, shareUrl, onShareComplete, handleDirectDownload]);

  const handleCopyLink = useCallback(async () => {
    try {
      if (typeof navigator !== 'undefined' && navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(shareUrl);
      } else if (typeof document !== 'undefined') {
        const textarea = document.createElement('textarea');
        textarea.value = shareUrl;
        textarea.style.position = 'fixed';
        textarea.style.opacity = '0';
        document.body.appendChild(textarea);
        textarea.focus();
        textarea.select();
        document.execCommand('copy');
        document.body.removeChild(textarea);
      }
      setCopied(true);
      onShareComplete?.('copylink');
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Fallback
    }
  }, [shareUrl, onShareComplete]);

  return (
    <div
      className={`flex flex-col justify-between w-full max-w-2xl mx-auto p-5 sm:p-6 bg-white border-2 border-slate-900 rounded-3xl shadow-xl shadow-slate-900/10 ${className}`}
    >
      {/* Header Bar */}
      <div>
        <div className="w-full flex items-center justify-between mb-2">
          <div className="flex items-center gap-2 text-slate-950 font-black text-base sm:text-lg font-display">
            <Share2 className="w-5 h-5 text-slate-900 shrink-0" />
            <span>Condividi con i tuoi Amici</span>
          </div>
          <span className="text-[11px] bg-slate-900 text-amber-300 px-2.5 py-0.5 rounded-full font-mono font-black">
            1080×1080 HD
          </span>
        </div>
        <p className="text-xs text-slate-600 font-semibold mb-4">
          Invia il verdetto su WhatsApp o scarica la card pronta per le storie Instagram.
        </p>

        {/* Compact, High-Contrast Canvas Preview */}
        <div className="relative w-full max-w-[260px] mx-auto aspect-square rounded-2xl overflow-hidden shadow-md border-2 border-slate-900 bg-white group">
          <canvas
            ref={canvasRef}
            width={1080}
            height={1080}
            className="w-full h-full object-contain cursor-pointer transition-transform duration-300 group-hover:scale-[1.02]"
            role="img"
            aria-label={`Scheda verdetto per ${prestationName} a ${provinceName}: ${calculationResult.zone}`}
            onClick={handleDirectDownload}
            title="Clicca per scaricare l'immagine in alta definizione"
          />
        </div>
      </div>

      {/* High-Contrast Action Buttons (Zero overlapping colors) */}
      <div className="grid grid-cols-2 gap-2.5 w-full mt-4">
        {/* 1. WhatsApp Button (Dark Emerald Green + Crisp White Text) */}
        <a
          href={whatsAppUrl}
          target="_blank"
          rel="noopener noreferrer"
          onClick={handleWhatsAppShare}
          className="col-span-2 sm:col-span-1 flex items-center justify-center gap-2 py-3 px-4 bg-[#16A34A] hover:bg-[#15803D] text-white font-black text-sm rounded-2xl border-2 border-slate-900 shadow-sm hover:shadow-md hover:-translate-y-0.5 active:translate-y-0.5 transition-all duration-150"
        >
          <svg className="w-4 h-4 fill-current shrink-0" viewBox="0 0 24 24" aria-hidden="true">
            <path d="M12.031 6.172c-3.181 0-5.767 2.586-5.768 5.766-.001 1.298.38 2.27 1.019 3.287l-.711 2.598 2.664-.698c.969.586 1.861.883 2.796.883 3.181 0 5.767-2.586 5.768-5.766 0-3.18-2.587-5.77-5.768-5.77zm0-2c4.298 0 7.781 3.483 7.781 7.77s-3.483 7.77-7.781 7.77c-1.332 0-2.585-.341-3.677-.938l-4.354 1.14 1.166-4.258c-.689-1.157-1.085-2.502-1.085-3.944 0-4.287 3.483-7.77 7.781-7.77z" />
          </svg>
          <span>Invia su WhatsApp</span>
        </a>

        {/* 2. Web Share / Condividi Button (Solid Dark Slate + Crisp White Text) */}
        <button
          type="button"
          onClick={handleWebShare}
          className="col-span-2 sm:col-span-1 flex items-center justify-center gap-2 py-3 px-4 bg-slate-900 hover:bg-slate-800 text-white font-black text-sm rounded-2xl border-2 border-slate-900 shadow-sm hover:shadow-md hover:-translate-y-0.5 active:translate-y-0.5 transition-all duration-150 cursor-pointer"
        >
          <Share2 className="w-4 h-4 shrink-0 text-amber-300" />
          <span>{canNativeShare ? 'Condividi Scheda' : 'Salva Immagine'}</span>
        </button>

        {/* 3. Direct Download PNG Button (White Background + Dark Slate Text) */}
        <button
          type="button"
          onClick={handleDirectDownload}
          className="flex items-center justify-center gap-2 py-2.5 px-3 bg-slate-50 hover:bg-amber-100 text-slate-950 text-xs sm:text-sm font-black rounded-2xl border-2 border-slate-900 shadow-sm hover:shadow transition-all duration-150 active:scale-[0.98] cursor-pointer"
        >
          <Download className="w-4 h-4 text-slate-900 shrink-0" />
          <span>Scarica PNG</span>
        </button>

        {/* 4. Copy Link Button (White/Emerald Background + Dark Slate Text) */}
        <button
          type="button"
          onClick={handleCopyLink}
          className={`flex items-center justify-center gap-2 py-2.5 px-3 text-xs sm:text-sm font-black rounded-2xl border-2 border-slate-900 shadow-sm hover:shadow transition-all duration-150 active:scale-[0.98] cursor-pointer ${
            copied
              ? 'bg-emerald-300 text-slate-950'
              : 'bg-slate-50 hover:bg-amber-100 text-slate-950'
          }`}
        >
          {copied ? (
            <Check className="w-4 h-4 text-slate-950 stroke-[3] shrink-0" />
          ) : (
            <Copy className="w-4 h-4 text-slate-900 shrink-0" />
          )}
          <span>{copied ? 'Link Copiato!' : 'Copia Link'}</span>
        </button>
      </div>
    </div>
  );
};

export default ShareCard;
