function [T] = uvToVec(u, v, R)

X = R*cos(v).*sin(u);
Y = R*sin(v).*sin(u);
Z = R*cos(u);
T = [X, Y, Z];
