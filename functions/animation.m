function [] = animation()
% move camera forward and render images
d=[1, 1, 0];
Cm = [0, 0, 1];

for i=1:20
    renderTorus(Cm, d, i);
    Cm=Cm+0.2.*d;
end