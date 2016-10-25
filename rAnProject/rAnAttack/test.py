from rAnProject.rAnet.ran_network import Ranet

g = Ranet()
g.load_network_from_snap_gp('100535338638690515335')
# g.load_network_from_sample()
# table = g.feature_rank([g.select_feat_by_name('rnd')], mode='entropy')
# g.block_analysis()
# print table
# print table.sort('count', ascending=False)
# g.prob_conn_by_feat('develop')
dt = g.get_feat_density_table()
print dt[dt['count'] >= 20].sort_values(by='density', ascending=False)