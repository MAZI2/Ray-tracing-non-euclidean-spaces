function [X, I] = cameraNew(d)
% Return array of vectors (rays) and image matrix
resolution_x = 1000;
resolution_y = 1000;
fov = 5;

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

        % if ray is completely horizontal, move it a little to displace
        % the sphere center, so that the correct direction can be retrieved
        % when moving in uv plane
        if(abs(ray(3))<0.0001)
            ray(3)=ray(3)+0.01;
        end
        X = [X ray'];
    end
end
I = zeros(resolution_y, resolution_x, 3);
