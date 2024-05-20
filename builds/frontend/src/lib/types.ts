export interface ImportCatalogEntry {
  status?: string;
  date_added?: string;
  original_name?: string;
  dataset_name?: string;
  dataset_id?: string;
  eeg_format?: string;
  eeg_paradigm?: string;
  is_set_file?: boolean;
  has_fdt_file?: boolean;
  fdt_filename?: string;
  fdt_upload_id?: string;
  hash?: string;
  upload_id: string;
  remove?: boolean;
  sample_rate?: number;
  n_channels?: number;
  n_epochs?: number;
  total_samples?: number;
  mne_load_error?: boolean;
}
export interface UploadCatalogEntry {
    status?: string;
    date_added?: string;
    original_name?: string;
    dataset_name?: string;
    dataset_id?: string;
    eeg_format?: string;
    eeg_paradigm?: string;
    is_set_file?: boolean;
    has_fdt_file?: boolean;
    fdt_filename?: string;
    fdt_upload_id?: string;
    hash?: string;
    upload_id: string;
    size?: string;
    remove_upload?: boolean;
}
export interface AnalysisJobListEntry {
  id: number;
  job_id?: string;
  upload_id?: string;
  eeg_format_name?: string;
  eeg_paradigm_name?: string;
  eeg_analysis_name?: string;
  status?: string;
  created_at?: Date;
  parameters?: string;
  result?: string;
}
export interface UploadedFile {
  data: {
    name: string;
    lastModified: number;
    lastModifiedDate: Date;
    webkitRelativePath: string;
    size: number;
    type: string;
  };
  extension: string;
  id: string;
  isGhost: boolean;
  isPaused: boolean;
  isRemote: boolean;
  meta: {
    eegFormat: string;
    eegParadigm: string;
    emailSelection: string;
    name: string;
    relativePath: string | null;
    type: string;
  };
  name: string;
  preview: string | undefined;
  progress: {
    uploadStarted: number;
    uploadComplete: boolean;
    percentage: number;
    bytesUploaded: number;
    bytesTotal: number;
  };
  remote: string;
  response: {
    uploadURL: string;
    status: number;
    body: object;
  };
  size: number;
  source: string;
  tus: {
    uploadUrl: string;
  };
  type: string;
  uploadURL: string;
}

export interface DBStats {
  message?: Record<string, any>;
}
export interface PortalPaths {
  message?: Record<string, string>;
}


export interface EEGFormat {
  id: string;
  name: string;
  description: string;
};

export interface UploadRow {
  status: string;
  date_added: string;
  original_name: string;
  dataset_name: string;
  dataset_id: string;
  eeg_format: string | null;
  eeg_paradigm: string | null;
  is_set_file: boolean | null;
  has_fdt_file: boolean | null;
  fdt_filename: string | null;
  fdt_upload_id: string | null;
  hash: string;
  upload_id: string;
  remove: boolean;
  size: string;
  upload_email: string | null;
}


export interface ImportRow {
  status: string;
  date_added: string;
  original_name: string;
  dataset_name: string;
  dataset_id: string;
  eeg_format: string | null;
  eeg_paradigm: string | null;
  is_set_file: boolean;
  has_fdt_file: boolean;
  fdt_filename: string;
  fdt_upload_id: string;
  hash: string;
  upload_id: string;
  remove: boolean;
  sample_rate: number;
  n_channels: number;
  n_epochs: number;
  total_samples: number;
  mne_load_error: boolean;
  upload_email: string | null;
}

export interface DatasetRow {
  dataset_name: string;
  dataset_id: string;
  description: string;
}

export interface DatasetStats {
  dataset_id: string;
  dataset_name: string;
  description: string;
  file_count: number;
}


