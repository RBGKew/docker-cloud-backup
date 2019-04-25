# Dockerhub

New builds are built automatically on dockerhub when a versioned tag is pushed to
github. For example

    git tag 0.1.9
    git push
    git push --tags

this will trigger a release tagged version 0.1.9 on dockerhub
