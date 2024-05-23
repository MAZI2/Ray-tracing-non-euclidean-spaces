function [X, I] = cameraNew()
resolution_x = 100;
resolution_y = 100;
fov = 5;

% direction
d=[1, 1, 0];

kot = atan(resolution_x / resolution_y);
fov_x = sin(kot) * fov;
fov_y = cos(kot) * fov;

kot_step = fov_x / resolution_x;

vec1=cross(d, [0, 0, -1]);
vec2=cross(vec1, d);
vec1=vec1./norm(vec1);
vec2=vec2./norm(vec2);

ray_direction = d+vec1.*(fov_x/2)-vec2.*(fov_y/2);
X=[];
for i=1:resolution_x
    for j=1:resolution_y
        ray=ray_direction + vec2.*(kot_step*j) - vec1.*(kot_step*i);
        % call ray tracing
        if(ray(3)==0)
            ray(3)=ray(3)+0.01;
        end
        X = [X ray'];
    end
end
I = zeros(resolution_y, resolution_x, 3);
