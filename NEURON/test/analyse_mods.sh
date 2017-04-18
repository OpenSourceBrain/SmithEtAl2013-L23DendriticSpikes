pynml-modchananalysis it -stepV 5 -temperature [26,34] -modFile '../mod.files/CaT.mod'
pynml-modchananalysis na -stepV 5 -temperature [26,34] -modFile '../mod.files/na.mod' -dt 0.001
pynml-modchananalysis ca -stepV 5 -temperature [26,34] -modFile '../mod.files/ca.mod'
pynml-modchananalysis kv -stepV 5 -temperature [26,34] -modFile '../mod.files/kv.mod'
pynml-modchananalysis km -stepV 5 -temperature [26,34] -modFile '../mod.files/km.mod'
pynml-modchananalysis kca -stepV 5 -temperature [26,34] -modFile '../mod.files/kca.mod' -caConc 5e-5 
