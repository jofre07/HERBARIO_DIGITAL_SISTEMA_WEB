export interface Collector {
  id: string;
  name: string;
  comment: string;
}

export interface CollectorWrite {
  name: string;
  comment?: string;
}
