function [val] = distPlane(T, A)
val = abs(A(1).*T(1)+A(2).*T(2)+A(3).*T(3)-A(4))./sqrt(A(1).^2+A(2).^2+A(3).^2);