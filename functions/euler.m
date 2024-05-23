function [y1t, y2t, y3t, y4t, h] = euler(y1p, y2p, y3p, y4p, h)
y1t = y1p + h*y2p;
y2t = y2p + h*cos(y1p).*sin(y1p).*(y4p.^2);
y3t = y3p + h*y4p;
y4t = y4p + h*-2.*cot(y1p).*y2p.*y4p;

if(y1t==0)
    h=h*2
    
    y1t=y1p;
    y2t=y2p;
    y3t=y3p;
    y4t=y4p;
    
end
