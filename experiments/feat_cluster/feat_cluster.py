import sys
sys.path.append("../..")
from rAnProject.rAnet.ran_network import Ranet

g = Ranet()
g.load_network_from_snap('100535338638690515335')
# g.load_network_from_snap('0', 'facebook')
# g.load_network_from_sample()
# table = g.feature_rank([g.select_feat_by_name('rnd')], mode='entropy')
# g.block_analysis()
# print table
# print table.sort('count', ascending=False)
# g.prob_conn_by_feat('develop')
dt, tdt = g.get_feat_density_table()
print tdt
print dt[dt['count'] >= 20].sort_values(by='density', ascending=False)

et, tet = g.get_feat_gcc_table()
print tet
print et[et['count'] >= 20].sort_values(by='gcc', ascending=False)

lt, tlt = g.get_feat_ave_lcc_table()
print tlt
print lt[lt['count'] >= 20].sort_values(by='lcc', ascending=False)

g.block_analysis(10)
