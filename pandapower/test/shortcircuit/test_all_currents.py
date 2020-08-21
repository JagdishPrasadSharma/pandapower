# -*- coding: utf-8 -*-

# Copyright (c) 2016-2020 by University of Kassel and Fraunhofer Institute for Energy Economics
# and Energy System Technology (IEE), Kassel. All rights reserved.


import numpy as np
import pytest

import pandapower as pp
import pandapower.shortcircuit as sc

@pytest.fixture
def three_bus_example():
    net = pp.create_empty_network()
    b1 = pp.create_bus(net, 110)
    b2 = pp.create_bus(net, 110)
    b3 = pp.create_bus(net, 110)

    pp.create_ext_grid(net, b1, s_sc_max_mva=100., s_sc_min_mva=80., rx_min=0.4, rx_max=0.4)
    pp.create_line(net, b1, b2, std_type="305-AL1/39-ST1A 110.0" , length_km=20.)
    pp.create_line(net, b2, b3, std_type="N2XS(FL)2Y 1x185 RM/35 64/110 kV" , length_km=15.)
    net.line["endtemp_degree"] = 80

    pp.create_sgen(net, b2, sn_mva=2, p_mw=0, k=1.2)
    return net


@pytest.fixture
def three_bus_permuted_index():
    net = pp.create_empty_network()
    b1 = pp.create_bus(net, 110, index=4)
    b2 = pp.create_bus(net, 110, index=3)
    b3 = pp.create_bus(net, 110, index=0)

    pp.create_ext_grid(net, b1, s_sc_max_mva=100., s_sc_min_mva=80., rx_min=0.4, rx_max=0.4)
    pp.create_line(net, b1, b2, std_type="305-AL1/39-ST1A 110.0" , length_km=20., index=1)
    pp.create_line(net, b2, b3, std_type="N2XS(FL)2Y 1x185 RM/35 64/110 kV" , length_km=15., index=0)
    net.line["endtemp_degree"] = 80

    pp.create_sgen(net, b2, sn_mva=2, p_mw=0, k=1.2)
    return net


@pytest.fixture
def gen_three_bus_example():
    net = pp.create_empty_network(sn_mva=2)
    b1 = pp.create_bus(net, vn_kv=10.)
    b2 = pp.create_bus(net, vn_kv=10.)
    b3 = pp.create_bus(net, vn_kv=10.)
    #pp.create_bus(net, vn_kv=0.4, in_service=False)
    pp.create_gen(net, b2, vn_kv=10.5, xdss_pu=0.2, rdss_pu=0.001, cos_phi=0.8, p_mw=0.1, sn_mva=2.5)
    pp.create_line_from_parameters(net, b1, b2, length_km=1.0, max_i_ka=0.29,
                                   r_ohm_per_km=0.1548, x_ohm_per_km=0.0816814, c_nf_per_km=165)
    pp.create_line_from_parameters(net, b2, b3, length_km=1.0, max_i_ka=0.29,
                                   r_ohm_per_km=0.1548, x_ohm_per_km=0.0816814, c_nf_per_km=165)
    net.line["endtemp_degree"] = 165
    pp.create_ext_grid(net, b1, s_sc_max_mva=10., s_sc_min_mva=8., rx_min=0.4, rx_max=0.4)
    #pp.create_switch(net, b3, b1, et="b")
    return net


def test_all_currents_sgen(three_bus_example):
    #
    # eg--0---l0---1---l1---2
    #              |
    #              g
    #
    net = three_bus_example
    sc.calc_sc(net, case="max", ip=True, ith=True, branch_results=True, return_all_currents=True)
    assert np.allclose(net.res_line_sc.ikss_ka.values,
                       np.array([0.01259673, 0.49593036, 0.48628848, 0., 0., 0.49888962]), atol=1e-5)
    assert np.allclose(net.res_line_sc.ip_ka.values,
                       np.array([0.01781447, 0.92787447, 0.90729584, 0., 0., 0.92511655]), atol=1e-5)
    assert np.allclose(net.res_line_sc.ith_ka.values,
                       np.array([0.01265116, 0.4981196, 0.48841266, 0., 0., 0.50106884]), atol=1e-5)

    sc.calc_sc(net, case="min", ip=True, ith=True, branch_results=True, return_all_currents=True)
    assert np.allclose(net.res_line_sc.ikss_ka.values,
                       np.array([0.01259673, 0.3989686, 0.39170662, 0., 0., 0.40431286]), atol=1e-5)
    assert np.allclose(net.res_line_sc.ip_ka.values,
                       np.array([0.01781447, 0.74438751, 0.72793774, 0., 0., 0.74576565]), atol=1e-5)
    assert np.allclose(net.res_line_sc.ith_ka.values,
                       np.array([0.01265116, 0.40071219, 0.39339323, 0., 0., 0.40605375]), atol=1e-5)


def test_with_permuted_index(three_bus_permuted_index):
    # Check that if element's index are permuted the results are still consistent
    #
    # eg--4---l1---3---l0---1
    #              |
    #              g
    #
    net = three_bus_permuted_index
    sc.calc_sc(net, case="max", ip=True, ith=True, branch_results=True, return_all_currents=True)
    assert np.allclose(net.res_line_sc.ikss_ka.loc[[(1, 4), (1, 3), (1, 0), (0, 4), (0, 3), (0, 0)]].values,
                       np.array([0.01259673, 0.49593036, 0.48628848, 0., 0., 0.49888962]), atol=1e-5)
    sc.calc_sc(net, case="min", ip=True, ith=True, branch_results=True, return_all_currents=True)
    assert np.allclose(net.res_line_sc.ikss_ka.loc[[(1, 4), (1, 3), (1, 0), (0, 4), (0, 3), (0, 0)]].values,
                       np.array([0.01259673, 0.3989686, 0.39170662, 0., 0., 0.40431286]), atol=1e-5)


def test_branch_all_currents_gen(gen_three_bus_example):
    net = gen_three_bus_example
    sc.calc_sc(net, case="max", branch_results=True, return_all_currents=True)
    assert np.allclose(net.res_line_sc.ikss_ka.values,
                       np.array([0.76204252, 0.57040645, 0.55786693, 0., 0., 1.28698045]))

    sc.calc_sc(net, case="min", branch_results=True, return_all_currents=True)
    assert np.allclose(net.res_line_sc.ikss_ka.values,
                       np.array([0.69255026, 0.45574755, 0.44487882, 0., 0., 1.10747517]))


if __name__ == '__main__':
    pytest.main(["test_all_currents.py"])
