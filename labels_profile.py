#%%
import pandas as pd

__all__ = ['chk_box_bhv_list', 'df_bhv_labels']

blackfirst = False

if blackfirst:
    bhv_labels = ['Back to back leaving',
        'Facial investigation',
        'Head to head approaching',
        'Circly sniffing',
        'Both rearing and facing away',
        'Cross by fast leaving',
        'Both rearing with facial investigation',
        'Back to back facing away',
        'Pinning with the partner full rotation',
        'Being fast chased',
        'Rearing with being back to back faced away',
        'Sniffing anogenital',
        'Pouncing from behind',
        'Pouncing from head',
        'Being slowly chased',
        'Rearing ahead a rearing partner (investigating back)',
        'Rearing and being faced away or leaved',
        'Watching (or approaching) the partner from behind',
        'Pouncing from behind and partner evading',
        'Pinning with the partner partial rotation',
        'Rearing with being watched',
        'Rearing with the partner in social range',
        'Being pinned and full rotation',
        'Fast chasing',
        'Back to back facing away the rearing partner',
        'Being sniffed at anogenital',
        'Being pounced from behind',
        'Being pounced from head',
        'Slow chasing',
        'Rearing behind a rearing partner (investigating back)',
        'Facing away or leaving a rearing partner',
        'Being watched (or approached) from behind',
        'Evading and being pounced from behind',
        'Being pinned with partial rotation',
        'Watching the rearing partner',
        'Sniffing the rearing partner']
else:
    bhv_labels = ['Back to back leaving',
        'Facial investigation',
        'Head to head approaching',
        'Circly sniffing',
        'Both rearing and facing away',
        'Cross by fast leaving',
        'Both rearing with facial investigation',
        'Back to back facing away',
        'Being pinned and full rotation',
        'Fast chasing',
        'Back to back facing away the rearing partner',
        'Being sniffed at anogenital',
        'Being pounced from behind',
        'Being pounced from head',
        'Slow chasing',
        'Rearing behind a rearing partner (investigating back)',
        'Facing away or leaving a rearing partner',
        'Being watched (or approached) from behind',
        'Evading and being pounced from behind',
        'Being pinned with partial rotation',
        'Watching the rearing partner',
        'Sniffing the rearing partner',
        'Pinning with the partner full rotation',
        'Being fast chased',
        'Rearing with being back to back faced away',
        'Sniffing anogenital',
        'Pouncing from behind',
        'Pouncing from head',
        'Being slowly chased',
        'Rearing ahead a rearing partner (investigating back)',
        'Rearing and being faced away or leaved',
        'Watching (or approaching) the partner from behind',
        'Pouncing from behind and partner evading',
        'Pinning with the partner partial rotation',
        'Rearing with being watched',
        'Rearing with the partner in social range']

df_bhv_labels = pd.DataFrame({'bhv_name': bhv_labels})
df_bhv_labels['cls_id'] = df_bhv_labels.index + 1
df_bhv_labels['id_bhv_name'] = '[' + df_bhv_labels['cls_id'].astype(str) + '] ' + df_bhv_labels['bhv_name']

chk_box_bhv_list = df_bhv_labels['id_bhv_name'].to_list()
