function [intersect, o] = exactIntersectTorus(T, d)
h = 0.13;
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

maxit = 300;%300;
step = 0;
intersect = [];
R = 2;
o = 0;
d = d./norm(d);
while true
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
   
    Tnt = Tn + h.*d;
    Tnt = mapToCube(Tnt, -3, 3);

    changed = 0;
    for i=1:objs
        if(sign(f(Tnt, O(:, i)', r(i))) == -signs(i))
            h=h./2;
            changed = 1;
            break
        end
    end
    
    if(changed == 0)
        Tn = Tnt;
        %plot3(Tn(1), Tn(2), Tn(3), 'ro');
        %hold on;
    end
    step = step+1;
end