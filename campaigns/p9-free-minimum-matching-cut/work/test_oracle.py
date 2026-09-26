from check import legal_source, solve_source, valid_source, legal_target, solve_target, valid_target


def test_hand_cases():
    edge = {"vertices":2,"edges":[[0,1]],"bound":1}
    assert valid_source(edge,{"side":[False,True]})
    assert valid_target(edge,{"side":[False,True]})
    assert solve_source({**edge,"bound":0}) == {"status":"NO-SOLUTION"}
    cycle = {"vertices":4,"edges":[[0,1],[1,2],[2,3],[0,3]],"bound":1}
    assert solve_target(cycle) == {"status":"NO-SOLUTION"}
    assert valid_target({**cycle,"bound":2},{"side":[False,False,True,True]})
    assert not valid_source(edge,{"side":[False,False]})
    path9 = {"vertices":9,"edges":[[i,i+1] for i in range(8)],"bound":1}
    assert legal_source(path9)
    assert not legal_target(path9)


if __name__ == "__main__":
    test_hand_cases()
