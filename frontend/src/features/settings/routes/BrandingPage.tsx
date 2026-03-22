import { useState, useEffect } from 'react'
import * as Sentry from '@sentry/react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Save, Upload, Smartphone, CheckCircle2, AlertCircle } from 'lucide-react'
import { brandingApi } from '../api/branding'
import { TenantBadge } from '@/shared/components/layout/TenantBadge'

export function BrandingPage() {
  const qc = useQueryClient()
  const { data: branding, isLoading, isError } = useQuery({ 
    queryKey: ['tenant-branding'], 
    queryFn: () => brandingApi.getBranding().then(r => (r as any).data || r) 
  })
  
  const updateMutation = useMutation({ 
    mutationFn: brandingApi.updateBranding, 
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['tenant-branding'] })
      setSaved(true)
      setTimeout(() => setSaved(false), 3000)
    } 
  })

  const uploadMutation = useMutation({
    mutationFn: brandingApi.uploadLogo,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['tenant-branding'] })
      setSaved(true)
      setTimeout(() => setSaved(false), 3000)
    }
  })

  const [appName, setAppName] = useState('')
  const [shortName, setShortName] = useState('')
  const [saved, setSaved] = useState(false)

  useEffect(() => {
    if (branding?.pwa_settings) {
      setAppName(branding.pwa_settings.app_name || '')
      setShortName(branding.pwa_settings.app_short_name || '')
    }
  }, [branding])

  if (isLoading) return <div className="p-8 text-text-muted animate-pulse">Loading branding settings...</div>
  if (isError) return <div className="p-8 text-status-error flex items-center gap-2"><AlertCircle size={18} /> Failed to load branding.</div>

  const handleSave = () => {
    updateMutation.mutate({ app_name: appName, app_short_name: shortName })
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      uploadMutation.mutate(file)
    }
  }

  const apiBase = import.meta.env.VITE_API_URL || ''

  return (
    <div className="flex flex-col h-full bg-bg-base animate-in fade-in duration-500">
      <header className="px-6 py-4 border-b border-sphotel-border bg-bg-surface/50 backdrop-blur-md sticky top-0 z-10 flex items-center justify-between">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-xl font-bold text-text-primary tracking-tight">App Branding</h1>
            <TenantBadge />
          </div>
          <p className="text-xs text-text-muted mt-0.5">Customize how your app looks on customer and staff devices.</p>
        </div>
        <div className="flex items-center gap-3">
          {saved && (
            <span className="flex items-center gap-1.5 text-status-success text-sm font-medium animate-in slide-in-from-right-2">
              <CheckCircle2 size={16} /> Saved Successfully
            </span>
          )}
          {/* TEMP: Sentry test button — remove after verifying Sentry captures frontend errors */}
          <button
            onClick={() => {
              const err = new Error('Sentry test error from BrandingPage')
              Sentry.captureException(err)
              console.error('[Sentry test] Error sent:', err.message)
            }}
            className="text-xs text-text-muted underline"
          >
            Test Sentry
          </button>
          <button 
            onClick={handleSave} 
            disabled={updateMutation.isPending}
            className="flex items-center gap-2 bg-sphotel-accent text-white px-5 py-2.5 rounded-xl text-sm font-semibold hover:shadow-lg hover:shadow-smarket-accent/20 active:scale-95 transition-all disabled:opacity-50"
          >
            <Save size={18} />
            {updateMutation.isPending ? 'Saving...' : 'Save Settings'}
          </button>
        </div>
      </header>

      <main className="flex-1 overflow-auto p-6 md:p-10">
        <div className="max-w-4xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-10">
          
          {/* Left Column: Form Settings */}
          <div className="flex flex-col gap-8">
            <section className="bg-bg-surface/30 border border-sphotel-border p-6 rounded-2xl backdrop-blur-sm shadow-sm group hover:border-sphotel-accent/50 transition-colors">
              <div className="flex items-center gap-3 mb-6">
                <div className="p-2 bg-sphotel-accent/10 rounded-lg text-sphotel-accent">
                  <Smartphone size={20} />
                </div>
                <h2 className="text-lg font-semibold text-text-primary">PWA Details</h2>
              </div>
              
              <div className="flex flex-col gap-5">
                <div className="space-y-2">
                  <label className="text-sm font-medium text-text-muted px-1">App Name</label>
                  <input 
                    type="text" 
                    value={appName}
                    onChange={e => setAppName(e.target.value)}
                    placeholder="e.g. My Awesome Restaurant"
                    className="w-full bg-bg-elevated border border-sphotel-border rounded-xl px-4 py-3 text-text-primary focus:outline-none focus:ring-2 focus:ring-sphotel-accent/50 focus:border-sphotel-accent transition-all placeholder:text-text-muted/50"
                  />
                  <p className="text-[10px] text-text-muted px-1">This name appears when installing the app on home screens.</p>
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium text-text-muted px-1">Short Name</label>
                  <input 
                    type="text" 
                    value={shortName}
                    onChange={e => setShortName(e.target.value)}
                    placeholder="e.g. My App"
                    maxLength={12}
                    className="w-full bg-bg-elevated border border-sphotel-border rounded-xl px-4 py-3 text-text-primary focus:outline-none focus:ring-2 focus:ring-sphotel-accent/50 focus:border-sphotel-accent transition-all placeholder:text-text-muted/50"
                  />
                  <p className="text-[10px] text-text-muted px-1">Maximum 12 characters. Used on small screens and app icons.</p>
                </div>
              </div>
            </section>

            <section className="bg-bg-surface/30 border border-sphotel-border p-6 rounded-2xl backdrop-blur-sm shadow-sm group hover:border-sphotel-accent/50 transition-colors">
              <div className="flex items-center gap-3 mb-4">
                <div className="p-2 bg-sphotel-accent/10 rounded-lg text-sphotel-accent">
                  <Upload size={20} />
                </div>
                <h2 className="text-lg font-semibold text-text-primary">App Logo</h2>
              </div>
              
              <p className="text-sm text-text-muted mb-6">Upload a high-resolution logo (512x512 recommended) for the PWA icon.</p>
              
              <div className="flex items-center gap-6">
                <div className="w-24 h-24 rounded-2xl bg-bg-elevated border-2 border-dashed border-sphotel-border flex items-center justify-center overflow-hidden relative group/logo">
                  {branding?.logo_path ? (
                    <img src={`${apiBase}/api/v1/public/logo/${branding.slug}.png?t=${Date.now()}`} alt="Current Logo" className="w-full h-full object-cover" />
                  ) : (
                    <img src={`${apiBase}/api/v1/public/logo/default.png`} alt="Default Logo" className="w-full h-full object-cover opacity-50" />
                  )}
                  <label className="absolute inset-0 bg-black/60 flex items-center justify-center opacity-0 group-hover/logo:opacity-100 transition-opacity cursor-pointer">
                    <input type="file" className="hidden" accept="image/*" onChange={handleFileChange} />
                    <Upload size={20} className="text-white" />
                  </label>
                </div>
                <div className="flex-1">
                  <button 
                    onClick={() => document.querySelector<HTMLInputElement>('input[type="file"]')?.click()}
                    className="text-sm font-semibold text-sphotel-accent hover:underline flex items-center gap-1"
                  >
                    Change Logo
                  </button>
                  <p className="text-[10px] text-text-muted mt-1">Supports PNG, JPG (SVG not recommended for PWA).</p>
                </div>
              </div>
            </section>
          </div>

          {/* Right Column: Preview */}
          <div className="lg:sticky lg:top-28 self-start">
             <div className="bg-bg-surface/50 border border-sphotel-border p-8 rounded-[3rem] shadow-2xl relative overflow-hidden ring-4 ring-bg-elevated">
                <div className="absolute top-2 left-1/2 -translate-x-1/2 w-20 h-5 bg-bg-elevated rounded-full"></div>
                
                <p className="text-center text-[10px] text-text-muted font-bold uppercase tracking-widest mb-10 mt-2">PWA INSTALL PREVIEW</p>
                
                <div className="flex flex-col items-center gap-6 py-8">
                  <div className="w-28 h-28 rounded-3xl bg-white shadow-xl flex items-center justify-center overflow-hidden border-4 border-bg-base/10 p-1">
                    {branding?.logo_path ? (
                       <img src={`${apiBase}/api/v1/public/logo/${branding.slug}.png?t=${Date.now()}`} alt="Preview" className="w-full h-full object-contain" />
                    ) : (
                       <img src={`${apiBase}/api/v1/public/logo/default.png`} alt="Preview" className="w-full h-full object-contain opacity-50" />
                    )}
                  </div>
                  
                  <div className="text-center space-y-1">
                    <h3 className="text-xl font-bold text-text-primary">{appName || 'My Restaurant'}</h3>
                    <p className="text-sm text-text-muted">https://{branding?.slug || 'your'}.sphotel.app</p>
                  </div>

                  <div className="mt-4 w-full bg-sphotel-accent/10 border border-sphotel-accent/20 p-4 rounded-2xl flex items-center justify-between">
                    <div>
                      <p className="text-xs font-bold text-text-primary italic">"Add to Home Screen"</p>
                      <p className="text-[10px] text-text-muted">This will look like a native app.</p>
                    </div>
                    <button className="bg-sphotel-accent text-white text-[10px] font-bold px-3 py-1.5 rounded-lg">INSTALL</button>
                  </div>
                </div>

                <div className="mt-12 flex justify-center pb-2">
                   <div className="w-12 h-1 bg-text-muted/20 rounded-full"></div>
                </div>
             </div>
          </div>

        </div>
      </main>
    </div>
  )
}
