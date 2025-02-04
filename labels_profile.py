#%%
import pandas as pd

__all__ = ['chk_box_bhv_list', 'chk_box_usv_list', 'df_bhv_labels', 'df_usv_labels']

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

bhv_modules = [[(2,12,26,4,22,36,18,32,8,1), 'Moderate'],
               [(11,25,21,35,17,31,5,7,16,30), 'Rear'],
               [(3,6,19,33,10,24,15,29), 'Chase'],
               [(13,27,14,28,9,23,20,34), 'Play']]

# bhv_modules = OrderedDict(bhv_modules)
# bhv_id_to_label = {i+1: bhv for i, bhv in enumerate(bhv_labels)}
# chk_box_bhv_collect = OrderedDict()
# for i, bhv in enumerate(bhv_labels):
#     chk_box_bhv_collect[f'[{i+1:>2}] {bhv}'] = i+1
# for id_l_, module_ in bhv_modules.items():
#     chk_box_bhv_collect[module_.upper()] = id_l_

bhv_modules = dict(bhv_modules)
df_bhv_labels = pd.DataFrame({'bhv_name': bhv_labels})
df_bhv_labels['cls_id'] = df_bhv_labels.index + 1
df_bhv_labels['module'] = ''
for id_l_, module_ in bhv_modules.items():
    df_bhv_labels.loc[df_bhv_labels['cls_id'].isin(id_l_), 'module'] = module_
df_bhv_labels['module'] = df_bhv_labels['module'].str.upper()
df_bhv_labels['id_bhv_name'] = '[' + df_bhv_labels['cls_id'].astype(str) + '] ' + df_bhv_labels['bhv_name']

# chk_box_bhv_list = list(map(str.upper, bhv_modules.values())) + df_bhv_labels['id_bhv_name'].to_list()
chk_box_bhv_list = df_bhv_labels['id_bhv_name'].to_list()

#%%
# usv_name, yolo_id, fig_id, cocluster_id, usv_module
df_usv_labels = pd.DataFrame([
    ['Split',10,10,1, 'Simple'],
    ['Inverted-U',6,5,2, 'Simple'],
    ['Complex',7,1,3, 'Simple'],
    ['Step up',8,2,4, 'Simple'],
    ['Short',2, 3,5, 'Simple'],
    ['Upward ramp',4,6,6, 'Simple'],
    ['Middle-flat', 0, 8,7, 'Flat'],
    ['Low-flat',1, 15,8, 'Flat'],
    ['Downward ramp',5,7,9, 'Flat'],
    ['Step down',9,	9,10, 'Flat'],
    ['Multi-short',3,4,11, 'Trills'],
    ['Multi-step',11,11,12, 'Trills'],
    ['Trill',12,12,13, 'Trills'],
    ['Step-trill',13,13,14, 'Trills'],
    ['Composite-trill',14,14,15, 'Trills']],
    columns=['usv_name', 'yolo_id', 'fig_id', 'cocluster_id', 'usv_module']
)
df_usv_labels.sort_values(by='fig_id', inplace=True)
df_usv_labels['id_usv_name'] = '[' + df_usv_labels['fig_id'].astype(str) + '] ' + df_usv_labels['usv_name']
df_usv_labels['usv_module'] = df_usv_labels['usv_module'].str.upper()
# chk_box_usv_list = ['SIMPLE', 'FLAT', 'TRILLS'] + df_usv_labels['id_usv_name'].to_list()
chk_box_usv_list = df_usv_labels['id_usv_name'].to_list()