FROM centos:centos6

ENV HOME /usr/local
ENV UFTHOME /opt


#############
   FFMPEG
#############

RUN yum -y install autoconf automake cmake freetype-devel gcc gcc-c++ git libtool make mercurial nasm pkgconfig zlib-devel tar

RUN mkdir /usr/local/src/ffmpeg_sources

RUN cd /usr/local/src/ffmpeg_sources && git clone --depth 1 git://github.com/yasm/yasm.git && cd yasm && autoreconf -fiv && ./configure --prefix="$HOME/ffmpeg_build" --bindir="$HOME/bin" && make && make install && make distclean

RUN cd /usr/local/src/ffmpeg_sources && git clone --depth 1 git://git.videolan.org/x264 && cd x264 && PKG_CONFIG_PATH="$HOME/ffmpeg_build/lib/pkgconfig" ./configure --prefix="$HOME/ffmpeg_build" --bindir="$HOME/bin" --enable-static && make && make install && make distclean

RUN cd /usr/local/src/ffmpeg_sources && hg clone https://bitbucket.org/multicoreware/x265 && cd /usr/local/src/ffmpeg_sources/x265/build/linux && cmake -G "Unix Makefiles" -DCMAKE_INSTALL_PREFIX="$HOME/ffmpeg_build" -DENABLE_SHARED:bool=off ../../source && make && make install

RUN cd /usr/local/src/ffmpeg_sources && git clone --depth 1 git://git.code.sf.net/p/opencore-amr/fdk-aac && cd fdk-aac && autoreconf -fiv && ./configure --prefix="$HOME/ffmpeg_build" --disable-shared && make && make install && make distclean

RUN cd /usr/local/src/ffmpeg_sources && curl -L -O http://downloads.sourceforge.net/project/lame/lame/3.99/lame-3.99.5.tar.gz && tar xzvf lame-3.99.5.tar.gz && cd lame-3.99.5 && ./configure --prefix="$HOME/ffmpeg_build" --bindir="$HOME/bin" --disable-shared --enable-nasm && make && make install && make distclean

RUN cd /usr/local/src/ffmpeg_sources && git clone git://git.opus-codec.org/opus.git && cd opus && autoreconf -fiv && ./configure --prefix="$HOME/ffmpeg_build" --disable-shared && make && make install && make distclean

RUN cd /usr/local/src/ffmpeg_sources && curl -O http://downloads.xiph.org/releases/ogg/libogg-1.3.2.tar.gz && tar xzvf libogg-1.3.2.tar.gz && cd libogg-1.3.2 && ./configure --prefix="$HOME/ffmpeg_build" --disable-shared && make && make install && make distclean

RUN cd /usr/local/src/ffmpeg_sources && curl -O http://downloads.xiph.org/releases/vorbis/libvorbis-1.3.4.tar.gz && tar xzvf libvorbis-1.3.4.tar.gz && cd libvorbis-1.3.4 && LDFLAGS="-L$HOME/ffmeg_build/lib" CPPFLAGS="-I$HOME/ffmpeg_build/include" ./configure --prefix="$HOME/ffmpeg_build" --with-ogg="$HOME/ffmpeg_build" --disable-shared && make && make install && make distclean

RUN cd /usr/local/src/ffmpeg_sources && git clone --depth 1 https://chromium.googlesource.com/webm/libvpx.git && cd libvpx && ./configure --prefix="$HOME/ffmpeg_build" --disable-examples && make && make install && make clean

RUN cd /usr/local/src/ffmpeg_sources && git clone --depth 1 git://source.ffmpeg.org/ffmpeg && cd ffmpeg && PKG_CONFIG_PATH="$HOME/ffmpeg_build/lib/pkgconfig" ./configure --prefix="$HOME/ffmpeg_build" --extra-cflags="-I$HOME/ffmpeg_build/include" --extra-ldflags="-L$HOME/ffmpeg_build/lib" --bindir="$HOME/bin" --pkg-config-flags="--static" --enable-gpl --enable-nonfree --enable-libfdk-aac --enable-libfreetype --enable-libmp3lame --enable-libopus --enable-libvorbis --enable-libvpx --enable-libx264 --enable-libx265 && make && make install && make distclean && hash -r


#########
   UFT
#########

RUN yum install -y epel-release

RUN yum install -y python-pip mediainfo mysql mysql-server gcc MySQL-python vim git syslog cronie

RUN pip install simple-json pymediainfo qtfaststart youtube-dl

RUN cd /opt && git clone https://github.com/supermasita/uft.git

#RUN /etc/init.d/mysqld start && mysql -e "CREATE DATABASE uft; CREATE USER 'uft'@'%' IDENTIFIED BY 'uft'; GRANT ALL PRIVILEGES ON uft.* TO 'uft'@'%' WITH GRANT OPTION; FLUSH PRIVILEGES;" && mysql -D uft < $UFTHOME/uft/lib/database_structure.sql
RUN /etc/init.d/mysqld start && mysql -D uft < $UFTHOME/uft/lib/database_structure.sql


