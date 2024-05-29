function [I] = render2Sphere(Cm, d, file)
% Driver function for whole image in 2-Sphere (almost the same as other two drivers)

% visualizing objects ----------
%{
C1 = [2, 2, -1];
%C2 = [0, 0, -2];
C2 = [4, 5, 0];

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
%plane
a=-0.2;
b=-0.2;
c=1;
dd=-3;

rangeX = [-15;15];
rangeY = [-15;15];
step = 2;

% define the range of x and y values
[x, y] = meshgrid(rangeX(1):step:rangeX(2), rangeY(1):step:rangeY(2));

% calculate corresponding z values using the plane equation
z = (dd - a*x - b*y) / c;

surf(x, y, z);
%}
%--------------------------------

% rays and image matrix
[X, I] = cameraNew(d);

% resoltion
res = 1000

% light source
%L=[-1, -1, -3];
L=[4, 2, 4];

% colors (2 spheres, 1 plane)
colors = [255 111 111; 0 128 255; 255 128 0];

k=1;
for i=1:res
    for j=1:res
        %if(j<151 && j>149 && mod(i,5)==0 && i<150)
            %plot3(X(1, k)+Cm(1),X(2, k)+Cm(2),X(3, k)+Cm(3), 'bo');
            [Int, o] = exactIntersect2Sphere(Cm, X(:, k)');
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
% save image to file instead of displaying it
%imwrite(I, append(int2str(file), "s.png"));