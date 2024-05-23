function [Tnt] = mapToCube(Tn, a, b)
range = b - a;
q = (Tn-a)./range;
fr = q - floor(q);
Tnt = a + fr.*range;