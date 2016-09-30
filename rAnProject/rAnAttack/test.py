from rAnProject.rAnAttack.rAnet.ran_network import Ranet

g = Ranet()
g.load_network_from_snap_gp('100535338638690515335')
table = g.feature_rank([g.select_feat_by_name('google')], mode='entropy')
g.block_analysis()
print table.sort('count', ascending=False)
