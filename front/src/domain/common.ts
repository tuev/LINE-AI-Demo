import {format} from 'date-fns';

export const formatTime = (t: Date) => format(t, 'yyyy-MM-dd HH:mm:ss');
