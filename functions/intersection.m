function [I] = intersection(maxit)
% Driver function for whole image in 2-Sphere

%{
d1 = [1, 0, 0];
d2 = [1, 0, 1];
d3 = [1, 1, 1];
d4 = [1, -1, -1];
%}

% visualizing sphere objects
C1 = [2, 2, -1];
C2 = [0, 0, -2];

%{
numPoints = 10;
[X, Y, Z] = sphere(numPoints);

X = 1*X + C1(1);
Y = 1*Y + C1(2);
Z = 1*Z + C1(3);

surf(X, Y, Z);
hold on

[X, Y, Z] = sphere(numPoints);

X = 0.5*X + C2(1);
Y = 0.5*Y + C2(2);
Z = 0.5*Z + C2(3);

surf(X, Y, Z);
%}
%-------------------------
% camera position
Cm = [0, 0, 1];
% rays
[X, I] = cameraNew();

res = 100

% light source
L=[-1, -1, -3];

% colors (2 spheres)
colors = [255 111 111; 0 128 255];

k=1;
for i=1:res
    for j=1:res
        %if(i==25 && (res-j<30 || res-j>70))
            %plot3(X(1, k)+Cm(1),X(2, k)+Cm(2),X(3, k)+Cm(3), 'bo');
            [Int, o] = exactIntersect(Cm, X(:, k)');
            if(norm(Int)>0)
                Lig = findLight(L, Int);
                if(Lig == -1)
                    I(j, i, 1)=colors(o, 1)/255;
                    I(j, i, 2)=colors(o, 2)/255;
                    I(j, i, 3)=colors(o, 3)/255;
                else
                    I(j, i, 1)=colors(o, 1)/255*0.5;
                    I(j, i, 2)=colors(o, 2)/255*0.5;
                    I(j, i, 3)=colors(o, 3)/255*0.5;
                end
            end
        %end
        
        k=k+1;
    end
end

imshow(I);