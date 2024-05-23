function [intersect, o] = exactIntersect(T, d)
% Ray trace for 2-Sphere
h = 0.1;
eps = 0.01;

% objects
% spheres
C1 = [2, 2, -1];
C2 = [0, 0, -2];
r1 = 1;
r2 = 0.5;
O = [C1' C2'];
r = [r1, r2];
objs = 2;
signs = [0, 0];
% for
signs(1) = sign(f(T, O(:, 1)', r(1)));
signs(2) = sign(f(T, O(:, 2)', r(2)));

Tn = T;
Tnt = Tn;

maxit = 100;%300;
step = 0;
intersect = [];
R = 2;
o = 0;
while true
    % in python make object.dist
    % for
    if(step == maxit)
        break
    end
    for i=1:objs
        if(dist(Tn, O(:, i)', r(i)) < eps)
            intersect = Tn;
            o = i;
            break
        end
    end
   
    % case 2sphere
    if(step == 0)
        Ce = sphereCenter(Tn, d, R);
        %plot3(Ce(1), Ce(2), Ce(3), 'go');
        %hold on
        Te = Tn-Ce;

        %u x.u
        y1p=acos(Te(3)./R);
        if(y1p==0)
            y1p=0.1;
        end
        %du, y.u fixed
        y2p=1;
        %v x.v
        y3p=atan2(Te(2), Te(1));
        %dv y.v
        y4p=0;

        [y1t, y2t, y3t, y4t, h] = euler(y1p, y2p, y3p, y4p, h);
        D = uvToVec(y1t, y3t, R)+Ce-Tn;
        if(d*D'<0)
            y2p=-1;
        end
        
    end
    [y1t, y2t, y3t, y4t, h] = euler(y1p, y2p, y3p, y4p, h);
    Tnt = uvToVec(y1t, y3t, R)+Ce;

    changed = 0;
    for i=1:objs
        if(sign(f(Tnt, O(:, i)', r(i))) == -signs(i)) % additional to if statement to make it more adaptive (if error is < eps)
            h=h./2;
            changed = 1;
            break
        end
    end
    
    if(changed == 0)
        y1p=y1t;
        y2p=y2t;
        y3p=y3t;
        y4p=y4t;
        Tn = Tnt;

        %plot3(Tn(1), Tn(2), Tn(3), 'ro');
    end
    step = step+1;
end
% ce bi iskali kake druge geodetke bi bilo bolje uporabiti DOPRI5, ampak
% deluje na Euler (1, 0) za nas primer.