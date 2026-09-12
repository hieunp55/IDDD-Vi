Khi Command Handler (bộ xử lý lệnh) hoàn tất, một thực thể Aggregate (Cụm Tổng hợp) đơn lẻ đã được cập nhật và một Domain Event (Sự kiện Miền) đã được công bố bởi command model (mô hình lệnh). Điều này đóng vai trò thiết yếu nhằm đảm bảo rằng query model (mô hình truy vấn) được cập nhật. Cũng cần lưu ý rằng, như đã được thảo luận trong Domain Events (Chương 8) và Aggregates (Chương 10), Event vừa công bố cũng có thể được sử dụng để kích hoạt sự đồng bộ hóa của các thực thể Aggregate khác bị ảnh hưởng bởi command duy nhất này, nhưng sự sửa đổi của các thực thể Aggregate bổ sung đó sẽ đạt được tính nhất quán sau cùng (eventual consistency) với thực thể đã được commit (chấp thuận lưu) bởi giao dịch này.

## Command Model (or Write Model) Executes Behavior

Khi mỗi phương thức command trên command model được thực thi, nó kết thúc bằng việc công bố một Event như được mô tả trong Domain Events (Chương 8). Sử dụng ví dụ xuyên suốt này, BacklogItem sẽ hoàn tất phương thức command của nó như sau:

```java
public class BacklogItem extends ConcurrencySafeEntity {
    ...
    public void commitTo(Sprint aSprint) {
        ...

```

```java
        DomainEventPublisher
            .instance()
            .publish(new BacklogItemCommitted(
                this.tenant(),
                this.backlogItemId(),
                this.sprintId()));
    }
    ...
}

```

## What's Behind the Publisher Component?

Thành phần DomainEventPublisher cụ thể này là một component mỏng nhẹ dựa trên Observer pattern (mẫu Người quan sát) [Gamma et al.]. Xem Domain Events (Chương 8) để biết chi tiết về cách các Event được công bố rộng rãi.

Đây là điểm then chốt (linchpin) để cập nhật query model với những thay đổi gần đây nhất từ command model. Nếu sử dụng Event Sourcing (Lưu trữ Sự kiện), các Event cũng là điều kiện cần thiết để lưu trữ trạng thái của Aggregate vừa được chỉnh sửa (trong ví dụ này là BacklogItem). Tuy nhiên, việc sử dụng Event Sourcing cùng với CQRS (Command-Query Responsibility Segregation - Phân tách Trách nhiệm Lệnh và Truy vấn) không phải là điều bắt buộc. Trừ khi việc ghi log Event là một yêu cầu được quy định rõ bởi phía nghiệp vụ, command model hoàn toàn có thể được lưu trữ bằng cách sử dụng một công cụ ORM (Object-Relational Mapping - Ánh xạ Đối tượng - Quan hệ) vào cơ sở dữ liệu quan hệ hoặc một cách tiếp cận nào khác. Dù theo cách nào, một Domain Event vẫn bắt buộc phải được công bố để đảm bảo rằng query model được cập nhật.

## When Commands Don't Result in Event Publishing

Có những trường hợp việc điều phối command không dẫn đến việc công bố Event. Ví dụ, nếu một command được chuyển phát bằng cơ chế truyền tin "at-least-once" (ít nhất một lần) và ứng dụng đảm bảo các thao tác mang tính lũy đẳng (idempotent), thì message gửi lại sẽ bị loại bỏ trong âm thầm (silently dropped).

Hãy xem xét cả trường hợp khi ứng dụng xác thực (validate) các command gửi đến. Tất cả các client hợp lệ đều nắm rõ các quy tắc xác thực và sẽ luôn vượt qua chúng. Tuy nhiên, tất cả các client trái phép — chẳng hạn như của kẻ tấn công — gửi các command không hợp lệ sẽ thất bại và có thể bị loại bỏ trong âm thầm mà không gây nguy hiểm cho những người dùng hợp lệ.

## Event Subscriber Updates the Query Model

Một subscriber (bên đăng ký nhận tin) đặc biệt đăng ký để tiếp nhận tất cả các Domain Event được công bố bởi command model. Subscriber này sử dụng từng Domain Event để cập nhật query model nhằm phản ánh những thay đổi mới nhất từ command model. Điều này hàm ý rằng mỗi Event phải đủ phong phú để cung cấp tất cả dữ liệu cần thiết nhằm tạo ra trạng thái chính xác bên trong query model.

Các bản cập nhật này nên được thực hiện đồng bộ (synchronously) hay bất đồng bộ (asynchronously)? Điều đó phụ thuộc vào mức tải thông thường của hệ thống, và có thể phụ thuộc cả vào vị trí lưu trữ cơ sở dữ liệu của query model. Các ràng buộc về tính nhất quán dữ liệu và các yêu cầu về hiệu năng sẽ chi phối quyết định này.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000136_8693c7ff48c18158ac92411fd16ca55b3d44a29a35e314e452e2aa2c86960155.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000137_9e4f1c6f30246914808af133e035942e76ad140962aad170600bf2178e0678bd.png)

Để cập nhật một cách đồng bộ, query model và command model thông thường sẽ dùng chung một cơ sở dữ liệu (hoặc cùng một schema), và chúng ta sẽ cập nhật cả hai mô hình trong cùng một giao dịch (transaction). Điều đó giữ cho cả hai mô hình hoàn toàn nhất quán. Tuy nhiên, điều này sẽ đòi hỏi nhiều thời gian xử lý hơn cho việc cập nhật nhiều bảng, điều có thể không đáp ứng được SLA (Service-Level Agreement - Cam kết Mức Dịch vụ). Nếu hệ thống thường xuyên chịu tải nặng và quy trình cập nhật query model kéo dài, hãy sử dụng cơ chế cập nhật bất đồng bộ thay thế. Điều này có thể dẫn đến những thách thức về tính nhất quán sau cùng, nơi giao diện người dùng sẽ không phản ánh ngay lập tức những thay đổi gần đây nhất trong command model. Thời gian trễ (lag time) là không thể dự đoán trước, nhưng đó là một sự đánh đổi (trade-off) có thể cần thiết để đáp ứng các SLA khác.

Điều gì sẽ xảy ra khi một giao diện hiển thị (view) mới được tạo ra trên giao diện người dùng nhưng dữ liệu của nó bắt buộc phải được tạo mới? Hãy thiết kế bảng và bất kỳ table view nào như đã mô tả trước đó. Điền dữ liệu trạng thái hiện tại vào bảng mới này bằng một trong vài kỹ thuật sau. Nếu command model được lưu trữ bằng Event Sourcing, hoặc nếu có một Event Store (Kho lưu trữ Sự kiện) chứa đầy đủ lịch sử, hãy phát lại (replay) các Event lịch sử để tạo ra các bản cập nhật. Điều này chỉ khả thi nếu các loại Event phù hợp đã tồn tại sẵn trong kho lưu trữ. Nếu không, bảng có thể sẽ phải được điền dữ liệu dần dần khi các command trong tương lai đi vào hệ thống. Ngoài ra, vẫn còn có một lựa chọn khác.

Nếu command model được lưu trữ bằng một công cụ ORM, hãy sử dụng kho lưu trữ của command model làm nguồn để nạp dữ liệu cho bảng query model mới. Cách này có thể áp dụng kỹ thuật sinh dữ liệu kho dữ liệu (hoặc cơ sở dữ liệu báo cáo) phổ biến, chẳng hạn như ETL (Extract, Transform, Load - Trích xuất, Chuyển đổi, Nạp). Trích xuất dữ liệu từ kho lưu trữ của command model, chuyển đổi dữ liệu đó theo nhu cầu của giao diện người dùng, và nạp nó vào kho lưu trữ của query model.

## Dealing with an Eventually Consistent Query Model

Nếu query model được thiết kế theo hướng nhất quán sau cùng — các bản cập nhật của query model được thực hiện bất đồng bộ sau các thao tác ghi vào kho lưu trữ command model — sẽ phát sinh những biểu hiện đặc thù (idiosyncrasies) trên giao diện người dùng cần phải xử lý. Ví dụ, sau khi người dùng gửi một command, liệu màn hình giao diện người dùng tiếp theo có phản ánh đầy đủ dữ liệu đã cập nhật và nhất quán từ query model hay không? Điều đó có thể phụ thuộc vào tải của hệ thống và các yếu tố khác. Nhưng tốt hơn hết chúng ta nên giả định là không và thiết kế cho tình huống xấu nhất, nơi giao diện người dùng không bao giờ ở trạng thái nhất quán tức thời.

Một lựa chọn là thiết kế giao diện người dùng tạm thời hiển thị dữ liệu đã được gửi thành công dưới dạng các tham số của command vừa được thực thi. Đây là một mẹo nhỏ, nhưng nó cho phép người dùng nhìn thấy ngay những gì cuối cùng sẽ được phản ánh trong query model. Đây có thể là cách duy nhất để đảm bảo rằng giao diện người dùng không hiển thị dữ liệu hoàn toàn cũ kỹ (stale data) ngay sau khi một command được thực thi thành công.

Điều gì sẽ xảy ra nếu giải pháp đó không khả thi đối với một giao diện người dùng nhất định? Ngay cả khi khả thi, vẫn có những thời điểm khi một người dùng bất kỳ thực thi một command và tất cả những người dùng khác đang xem dữ liệu liên quan chắc chắn sẽ nhìn thấy dữ liệu cũ. Làm thế nào để giải quyết thách thức này?

Một kỹ thuật được [Dahan, CQRS] đề xuất là luôn hiển thị rõ ràng trên giao diện người dùng ngày và giờ của dữ liệu từ query model mà người dùng hiện đang xem. Để làm được điều này, mỗi bản ghi trong query model cần duy trì ngày và giờ của lần cập nhật mới nhất. Đây là một bước đơn giản, thường được hỗ trợ bởi một database trigger (bộ kích hoạt cơ sở dữ liệu). Với ngày và giờ của lần cập nhật mới nhất, giao diện người dùng giờ đây có thể thông báo cho người dùng biết dữ liệu đã cũ bao nhiêu lâu. Nếu người dùng nhận thấy dữ liệu đã quá cũ để sử dụng, họ có thể yêu cầu lấy dữ liệu mới hơn tại thời điểm đó. Phải thừa nhận rằng cách tiếp cận này được một số người ca ngợi như một mẫu thiết kế hiệu quả nhưng lại bị những người khác chỉ trích nặng nề như một giải pháp chắp vá (hack) hay một thủ thuật gượng ép. Chắc chắn những quan điểm đối lập này chỉ ra sự cần thiết phải thực hiện các bài kiểm thử chấp nhận người dùng (user acceptance tests - UAT) trước khi cách tiếp cận này được đưa vào sử dụng trong hệ thống của chúng ta.

Dẫu vậy, hoàn toàn có khả năng sự chậm trễ trong việc đồng bộ hóa dữ liệu hiển thị không phải là một vấn đề nghiêm trọng. Nó cũng có thể được khắc phục bằng các phương tiện khác, chẳng hạn như Comet (còn gọi là Ajax Push), hoặc một hình thức cập nhật ngầm khác, chẳng hạn như một biến thể nào đó của Observer [Gamma et al.] hoặc cơ chế đăng ký nhận sự kiện từ Distributed Cache/Grid (Bộ nhớ đệm phân tán/Lưới tính toán - ví dụ: Coherence hoặc GemFire). Việc xử lý sự chậm trễ thậm chí có thể đơn giản chỉ là thông báo cho người dùng biết rằng yêu cầu của họ đã được tiếp nhận và kết quả sẽ cần một khoảng thời gian xử lý nhất định. Hãy xác định cẩn trọng xem liệu thời gian trễ của tính nhất quán sau cùng có gây ra vấn đề hay không. Nếu có, bạn sẽ phải tìm ra cách tốt nhất để giải quyết nó trong một môi trường cụ thể.

Giống như mọi pattern khác, CQRS đưa vào một số yếu tố xung đột và cạnh tranh lẫn nhau. Chúng ta phải hết sức cẩn trọng và đưa ra lựa chọn khôn ngoan. Chắc chắn nếu một giao diện người dùng không quá phức tạp hoặc không thường xuyên cắt ngang qua nhiều Aggregate khác nhau trong một màn hình hiển thị duy nhất, thì việc áp dụng CQRS sẽ chỉ làm phát sinh accidental complexity (độ phức tạp ngẫu sinh) thay vì necessary complexity (độ phức tạp cần thiết). CQRS chỉ là lựa chọn đúng đắn khi nó loại bỏ được một rủi ro có xác suất cao gây ra thất bại nếu bị phớt lờ.

## Event-Driven Architecture

> Kiến trúc hướng sự kiện (EDA - Event-Driven Architecture) là một kiến trúc phần mềm thúc đẩy việc sản xuất, phát hiện, tiêu thụ và phản ứng đối với các sự kiện. [Wikipedia, EDA]

Hexagonal Architecture (Kiến trúc Lục giác) được thể hiện trong Hình 4.4 có thể đại diện cho khái niệm về một hệ thống tham gia vào một EDA thông qua các message gửi đến và gửi đi. Một EDA không nhất thiết phải sử dụng Hexagonal, nhưng đó là một cách tiếp cận thỏa đáng để trình bày các khái niệm ở đây. Đối với một dự án làm mới từ đầu (greenfield project), việc cân nhắc sử dụng Hexagonal làm phong cách bao quát tổng thể là rất đáng giá.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000138_04d2d39e6492fef9a3ac127cee3d36233584817c56a4bb5eac1c022cb57c74e7.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000139_03db5ddfcc4069ec2c6367e56fa7cdef490330edaef95f4399a3aef17ca1c6d8.png)

Quan sát Hình 4.4, giả sử client hình tam giác và cơ chế đầu ra hình tam giác tương ứng đại diện cho cơ chế messaging được sử dụng bởi Bounded Context (Ngữ cảnh Ranh giới). Các sự kiện đầu vào đi vào qua một Port (Cổng) riêng biệt so với Port được ba client kia sử dụng. Các sự kiện đầu ra tương tự cũng đi qua một Port khác. Như đã đề xuất trước đây, các Port riêng biệt này có thể đại diện cho việc vận chuyển message qua AMQP (Advanced Message Queuing Protocol - Giao thức Hàng đợi Thông điệp Nâng cao), như được sử dụng bởi RabbitMQ, thay vì giao thức HTTP phổ biến hơn mà các client khác sử dụng. Bất kể cơ chế messaging thực tế nào đang được sử dụng, chúng ta sẽ giả định rằng các sự kiện đi vào và đi ra khỏi hệ thống thông qua các hình tam giác mang tính biểu tượng này.

Có thể có một số loại sự kiện khác nhau đi vào và đi ra khỏi một hình lục giác. Chúng ta đặc biệt quan tâm đến các Domain Event. Ứng dụng cũng có thể đăng ký nhận các sự kiện hệ thống, sự kiện doanh nghiệp hoặc các loại sự kiện khác. Có thể những sự kiện đó xử lý tình trạng và giám sát hệ thống, ghi log, cấp phát tài nguyên động và những tác vụ tương tự. Dẫu vậy, chính các Domain Event mới là thứ truyền tải những diễn biến đòi hỏi sự chú ý trong mô hình hóa của chúng ta.

Chúng ta có thể nhân bản hệ thống trong khung nhìn Hexagonal Architecture bao nhiêu lần tùy ý để đại diện cho toàn bộ các hệ thống trong doanh nghiệp hỗ trợ phong cách Event-Driven. Điều đó đã được thực hiện trong Hình 4.7. Một lần nữa, điều này không có nghĩa là mọi hệ thống đều sẽ dựa trên Hexagonal. Sơ đồ chỉ chứng minh cách thức Event-Driven có thể được hỗ trợ nếu nhiều hệ thống lấy Hexagonal làm nền tảng của chúng. Nếu không, bạn hoàn toàn có thể thay thế các hình lục giác bằng Layers (Kiến trúc Phân tầng), hoặc một phong cách kiến trúc khác.

Các Domain Event được công bố bởi một hệ thống như vậy thông qua Port đầu ra sẽ được chuyển phát tới các subscriber được đại diện ở những hệ thống khác thông qua Port đầu vào của chúng. Các Domain Event khác nhau nhận được mang một ý nghĩa cụ thể trong từng Bounded Context tiếp nhận, hoặc có thể hoàn toàn không mang ý nghĩa nào cả. [^5] Nếu loại Event đó được một Context cụ thể quan tâm, các thuộc tính của nó sẽ được chuyển đổi cho phù hợp với API của ứng dụng và được sử dụng để thực thi một thao tác tại đó. Thao tác command được thực thi trên API của ứng dụng sau đó sẽ được phản ánh vào mô hình miền theo đúng giao thức của nó.

Hình 4.7 Ba hệ thống sử dụng Kiến trúc Hướng Sự kiện với phong cách Hexagonal bao quát. Phong cách EDA tách rời mọi sự phụ thuộc của các hệ thống ngoại trừ sự phụ thuộc vào chính cơ chế messaging và các kiểu Event mà chúng đăng ký nhận tin.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000140_409c7f73e00848fe24e830a6bf11a0d25f6e9980eb9f06c949803f3d5bd71993.png)

Hoàn toàn có khả năng một Domain Event cụ thể nhận được chỉ đại diện cho một phần của một quy trình đa tác vụ (multitask process). Cho đến khi tất cả các Domain Event dự kiến đến đủ, quy trình đa tác vụ đó mới được coi là hoàn tất. Nhưng quy trình đó bắt đầu như thế nào? Nó được phân tán trên toàn doanh nghiệp ra sao? Và làm cách nào chúng ta theo dõi tiến độ cho đến khi quy trình hoàn thành? Câu trả lời sẽ được thảo luận ở phần sau trong mục về các tiến trình chạy lâu dài (long-running processes). Nhưng trước tiên, việc đặt nền tảng ban đầu là cần thiết. Các hệ thống dựa trên thông điệp thường phản ánh phong cách Pipes and Filters (Ống dẫn và Bộ lọc).

## Pipes and Filters

Ở một trong những dạng thức đơn giản nhất, Pipes and Filters có thể sử dụng thông qua dòng lệnh shell/console:

```bash
$cat phone_numbers.txt \vert{} grep 303 \vert{} wc -l 3$

```

Ở đây, dòng lệnh Linux được sử dụng để tìm xem có bao nhiêu liên hệ trong trình quản lý thông tin cá nhân cao cấp, `phone_numbers.txt`, sở hữu số điện thoại tại Colorado. Phải thừa nhận rằng đây không phải là một cách rất đáng tin cậy để triển khai use case đó, nhưng nó chứng minh cách thức hoạt động của Pipes and Filters:

1. Tiện ích `cat` xuất nội dung của `phone_numbers.txt` ra luồng dữ liệu gọi là luồng đầu ra tiêu chuẩn (standard output stream). Thông thường luồng này được kết nối với màn hình console. Nhưng khi ký hiệu `|` được sử dụng, đầu ra sẽ được dẫn qua đường ống (piped) tới đầu vào của tiện ích tiếp theo.
2. Tiếp theo, `grep` đọc đầu vào của nó từ luồng đầu vào tiêu chuẩn (standard input stream), vốn là kết quả từ `cat`. Đối số truyền cho `grep` yêu cầu nó khớp các dòng có chứa văn bản `303`. Mỗi dòng tìm thấy sẽ được xuất ra luồng đầu ra tiêu chuẩn của nó. Tương tự như với `cat`, luồng đầu ra của `grep` giờ đây lại được dẫn qua ống tới đầu vào của tiện ích tiếp theo.
3. Cuối cùng, `wc` đọc luồng đầu vào tiêu chuẩn của nó, vốn được dẫn từ luồng đầu ra tiêu chuẩn của `grep`. Đối số dòng lệnh truyền cho `wc` là `-l`, yêu cầu nó đếm số dòng mà nó đọc được. Nó xuất ra kết quả, trong trường hợp này

[^5]: Nếu sử dụng các bộ lọc thông điệp (message filters) hoặc các routing key (khóa định tuyến), các subscriber có thể tránh được việc nhận các Event vô nghĩa đối với chúng.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000141_743228c006af2e6099d12f3da07772b4c207750e64b0fe78d0a8698975393a16.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000142_7ff5450e93b521bb669adc286984bf43497bf7d3b7c61d42e5727c9fb6239.png)

là `3`, bởi vì có ba dòng đã được xuất ra bởi `grep`. Lưu ý rằng giờ đây đầu ra tiêu chuẩn được hiển thị ra console vì lần này không còn Pipe nào dẫn tới một lệnh bổ sung nào khác nữa.

Điều này có thể được mô phỏng tương tự trên console Windows, nhưng sử dụng ít đường ống hơn:

```cmd
C:\fancy_pim> type phone_numbers.txt | find /c "303" 3 C:\fancy_pim>

```

Hãy xem xét những gì diễn ra với từng tiện ích. Mỗi tiện ích nhận một tập dữ liệu, xử lý nó, và xuất ra một tập dữ liệu khác. Tập dữ liệu xuất ra có sự thay đổi so với dữ liệu đầu vào bởi vì mỗi tiện ích đóng vai trò như một Filter (Bộ lọc). Đến cuối quy trình lọc, đầu ra hoàn toàn khác biệt so với đầu vào. Đầu vào ban đầu là một tệp văn bản với các dòng thông tin liên hệ riêng lẻ và kết thúc là chữ số văn bản đại diện cho số 3.

Sử dụng các nguyên lý cơ bản từ ví dụ này, làm thế nào chúng ta có thể áp dụng chúng vào một Kiến trúc Hướng Sự kiện? Trên thực tế, chúng ta có thể tìm thấy một số điểm giao thoa hữu ích. Cuộc thảo luận sau đây dựa trên pattern truyền thông điệp Pipes and Filters trong [Hohpe, Woolf]. Tuy nhiên, hãy hiểu rằng cách tiếp cận Pipes and Filters dựa trên thông điệp không hoàn toàn giống hệt phiên bản dòng lệnh, và nó cũng không nhằm mục đích làm điều đó. Ví dụ, một Filter trong EDA không nhất thiết phải thực sự lọc bỏ thứ gì. Một Filter trong EDA có thể được sử dụng để thực hiện một số bước xử lý trong khi vẫn giữ nguyên vẹn dữ liệu của message. Dẫu vậy, Pipes and Filters trong EDA đủ tương đồng với kiểu dòng lệnh để ví dụ trước đó giúp tạo dựng nền tảng cho những gì tiếp theo. Nếu bạn là người đọc đã có kinh nghiệm nâng cao, hãy thoải mái "lọc" bỏ những nội dung dưới đây.

Bảng 4.2 trình bày một số đặc tính cơ bản của một quy trình Pipes and Filters dựa trên message.

Bảng 4.2 Các Đặc tính Cơ bản của một Quy trình Pipes and Filters Dựa trên Message

| Đặc tính | Mô tả |
| --- | --- |
| Pipes là các message channels (kênh thông điệp) | Các Filter nhận message trên một Pipe đầu vào và gửi message trên một Pipe đầu ra. Pipe thực chất chính là một message channel. |
| Ports kết nối các Filter với các Pipe | Các Filter kết nối với các Pipe đầu vào và đầu ra thông qua một Port. Các Port khiến Hexagonal (Ports and Adapters) trở thành một phong cách bao quát rất phù hợp. |
| Filters là các bộ xử lý (processors) | Các Filter có thể xử lý message mà không nhất thiết phải thực sự lọc bỏ dữ liệu. |
| Các bộ xử lý tách biệt | Mỗi bộ xử lý Filter là một component riêng biệt, và độ hạt thành phần (component granularity) phù hợp đạt được thông qua thiết kế cẩn trọng. |

Bảng 4.2 Các Đặc tính Cơ bản của một Quy trình Pipes and Filters Dựa trên Message (Tiếp theo)

| Đặc tính | Mô tả |
| --- | --- |
| Liên kết lỏng (Loosely coupled) | Mỗi bộ xử lý Filter được cấu thành vào quy trình một cách độc lập với tất cả các bộ xử lý khác. Sự kết hợp các bộ xử lý Filter có thể được định nghĩa bằng cấu hình. |
| Có thể hoán đổi cho nhau (Interchangeable) | Thứ tự nhận message của một bộ xử lý có thể được sắp xếp lại tùy theo yêu cầu của use case, một lần nữa thông qua việc cấu hình cấu trúc liên kết. |
| Filters có thể đa Pipe (multi-Pipe) | Trong khi các Filter dòng lệnh chỉ đọc từ và ghi vào một Pipe duy nhất, các Filter dạng thông điệp có thể đọc từ và/hoặc ghi vào nhiều Pipe, hàm ý khả năng xử lý song song hoặc đồng thời. |
| Sử dụng các Filter cùng loại song song | Những Filter bận rộn nhất và có thể chậm nhất có thể được triển khai thành nhiều thực thể để gia tăng thông lượng (throughput). |

Bây giờ, điều gì sẽ xảy ra nếu chúng ta coi mỗi tiện ích `cat`, `grep`, và `wc` (hoặc `type` và `find`) như các component trong một Kiến trúc Hướng Sự kiện? Điều gì sẽ xảy ra nếu chúng ta thậm chí triển khai các component đóng vai trò là bên gửi và bên nhận message để xử lý các số điện thoại theo cách tương tự? (Một lần nữa, tôi không cố gắng minh họa một sự thay thế 1-1 cho dòng lệnh, mà chỉ là một ví dụ truyền thông điệp đơn giản với các mục tiêu cơ bản tương đương.)

Dưới đây là cách thức một giải pháp Pipes and Filters dựa trên thông điệp có thể vận hành, với các bước được minh họa trong Hình 4.8:

1. Chúng ta có thể bắt đầu với một component có tên `PhoneNumbersPublisher`, nó đọc tất cả các dòng trong `phone_numbers.txt` rồi tạo và gửi một message Event bao gồm tất cả các dòng văn bản đó. Event này có tên là `AllPhoneNumbersListed`. Một khi nó được gửi đi, pipeline (đường ống dẫn xử lý) bắt đầu hoạt động.
2. Một component xử lý message có tên `PhoneNumberFinder` được cấu hình để đăng ký nhận `AllPhoneNumbersListed` và tiếp nhận nó. Component xử lý message này là Filter đầu tiên trong pipeline. Filter này được cấu hình để tìm kiếm chuỗi văn bản `303`. Component này xử lý Event bằng cách tìm kiếm chuỗi ký tự `303` trên từng dòng. Sau đó, nó tạo một Event mới có tên `PhoneNumbersMatched`, đưa toàn bộ các dòng kết quả khớp vào Event. Message Event này được gửi đi, tiếp tục chu trình của pipeline.
3. Một component xử lý message có tên `MatchedPhoneNumberCounter` được cấu hình để đăng ký nhận `PhoneNumbersMatched` và tiếp nhận nó. Component xử lý message này là Filter thứ hai trong pipeline. Trách nhiệm duy nhất của nó

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000143_1d3d77d06ca408e61f1d8a34ac5bd450f2ee8dc7d4406d4cdcc99079dc050001.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000144_eb3d73ba8f832c10082175cfacfd66173102c9e47258248450121c28f30f4162.png)

Hình 4.8 Một pipeline được tạo thành bằng cách gửi các Event mà các Filter sẽ xử lý.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000145_a981e7587740ff5daed7fada9d840a127e12a0d8fb669ef4ab79fe7d8e923068.png)

là đếm các số điện thoại có trong Event và sau đó chuyển tiếp kết quả trong một Event mới. Trong trường hợp này, nó đếm được tổng cộng ba dòng chứa số điện thoại. Filter hoàn tất bằng cách tạo ra Event `MatchedPhoneNumbersCounted`, gán thuộc tính `count` thành `3`. Message Event này được gửi đi, tiếp tục chu trình của pipeline.
4. Cuối cùng, một component xử lý message đã đăng ký nhận `MatchedPhoneNumbersCounted` sẽ tiếp nhận nó. Component này có tên là `PhoneNumberExecutive`. Trách nhiệm duy nhất của nó là ghi log kết quả ra tệp, bao gồm thuộc tính `count` của Event cùng ngày giờ nhận được. Trong trường hợp này, nó ghi:
5. 3 phone numbers matched on July 15, 2012 at 11:15 PM (3 số điện thoại khớp vào ngày 15 tháng 7 năm 2012 lúc 11:15 CH)

Pipeline cho quy trình cụ thể này hiện đã hoàn tất. [^6]

[^6]: Để đơn giản hóa, tôi không thảo luận về Ports, Adapters, và API ứng dụng của Hexagonal Architecture.

Kiểu pipeline này tương đối linh hoạt. Nếu muốn thêm bất kỳ Filter mới nào vào pipeline, chúng ta sẽ tạo các Event mới mà mỗi Filter hiện có sẽ đăng ký nhận và công bố. Về cơ bản, chúng ta sẽ phải thay đổi thứ tự tuần tự của pipeline một cách cẩn thận thông qua cấu hình. Tất nhiên, việc thay đổi quy trình này không dễ dàng như với phương pháp dòng lệnh. Tuy nhiên, thông thường chúng ta sẽ không thay đổi các pipeline Domain Event thường xuyên đến vậy. Mặc dù bản thân quy trình phân tán cụ thể này không mang lại nhiều giá trị thực tiễn, nó minh họa rõ nét cách thức Pipes and Filters có thể hoạt động trong một Kiến trúc Hướng Sự kiện dựa trên thông điệp.

Vậy, liệu chúng ta có thực sự kỳ vọng sẽ thấy Pipes and Filters được khai thác để giải quyết một bài toán như thế này không? Lý tưởng nhất là không. (Trên thực tế, nếu bạn cảm thấy ví dụ này gây phiền toái, có lẽ là vì bạn đã nắm quá rõ rồi. Điều đó rất tốt, nhưng có rất nhiều người khác được hưởng lợi từ nó.) Ví dụ này chỉ nhằm mục đích minh họa tổng hợp, làm nổi bật các khái niệm. Trong một doanh nghiệp thực tế, chúng ta sẽ sử dụng pattern này để chia nhỏ một bài toán lớn thành các bước nhỏ hơn giúp việc xử lý phân tán trở nên dễ hiểu và dễ quản lý hơn. Nó cũng cho phép nhiều hệ thống chỉ cần tập trung làm tốt những gì thuộc thế mạnh của chúng.

Trong một kịch bản DDD thực tế, các Domain Event phản ánh những cái tên có ý nghĩa đối với nghiệp vụ. Bước 1 có thể công bố một Domain Event dựa trên kết quả hành vi của một Aggregate trong một Bounded Context. Các bước từ 2 đến 4 có thể diễn ra trong một hoặc nhiều Bounded Context khác nhau nhận Event ban đầu và sau đó công bố một trong các Event tiếp theo. Ba bước đó có thể tạo mới hoặc sửa đổi các Aggregate trong các Context tương ứng của chúng. Điều đó phụ thuộc vào miền nghiệp vụ, nhưng đó là những kết quả phổ biến khi xử lý các Domain Event trong một Kiến trúc Pipes and Filters.

Như đã giải thích trong Domain Events (Chương 8), đây không chỉ là những thông báo kỹ thuật mỏng như tờ giấy. Chúng mô hình hóa một cách tường minh các diễn biến hoạt động của quy trình nghiệp vụ vốn rất hữu ích cho các subscriber trong toàn miền nhận biết, và chúng chứa đựng định danh duy nhất cùng nhiều thuộc tính truyền tải tri thức cần thiết để làm rõ thông điệp của mình. Dẫu vậy, phong cách đồng bộ từng bước này có thể được mở rộng để thực hiện nhiều công việc cùng một lúc.

## Long-Running Processes, aka Sagas

Ví dụ tổng hợp về Pipes and Filters có thể được mở rộng để minh họa một pattern xử lý song song, phân tán, hướng sự kiện khác, cụ thể là: Long-Running Processes (Các Tiến trình Chạy Lâu dài). Một Long-Running Process đôi khi được gọi là một Saga, nhưng tùy thuộc vào nền tảng của bạn, tên gọi đó có thể xung đột với một pattern đã tồn tại từ trước. Mô tả ban đầu về Saga được trình bày trong [Garcia-Molina & Salem]. Nhằm nỗ lực tránh sự nhầm lẫn và mơ hồ, tôi chọn sử dụng tên gọi Long-Running Process, và đôi khi tôi dùng tên Process cho ngắn gọn.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000146_61f96fc7e1d47095ec52ba374e14a9c235e8fe16fd3e6c7230004064bb80d6bb.png)

## Cowboy Logic

* LB: 'Dallas và Dynasty, đó mới đích thị là những gì tôi gọi là các saga (phim dài tập trường thiên)!'
* AJ: 'Dành cho tất cả độc giả người Đức, các bạn đều biết Dynasty dưới cái tên Der Denver Clan.'

> 💡 **Giải thích thêm:** "Dallas" và "Dynasty" là hai bộ phim truyền hình dài tập (soap operas) kinh điển của Mỹ phát sóng vào thập niên 1980, kể về những mâu thuẫn gia tộc và thương trường kéo dài hàng trăm tập qua nhiều năm. Tại Đức, phim "Dynasty" được phát sóng dưới tên "Der Denver Clan". Đây là phép chơi chữ dí dỏm giữa từ "saga" trong văn hóa đại chúng (phim truyền hình dài tập, trường thiên kịch nhiều kỳ) và thuật ngữ kỹ thuật "Saga / Long-Running Process" trong hệ thống phân tán (tiến trình nghiệp vụ phức tạp kéo dài qua nhiều bước và nhiều hệ thống).
> Nguồn tham khảo: [Wikipedia - Dynasty (1981 TV series)](https://en.wikipedia.org/wiki/Dynasty_(1981_TV_series))

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000147_b25b49625e45e2b7d14d2a32881bb7415c4b6a2d50e4cd403896c0b6080872b5.png)

Mở rộng ví dụ trước, chúng ta có thể tạo ra các pipeline song song bằng cách chỉ cần thêm một Filter mới duy nhất, `TotalPhoneNumbersCounter`, làm subscriber bổ sung cho `AllPhoneNumbersListed`. Nó nhận Event `AllPhoneNumbersListed` gần như song song với `PhoneNumberFinder`. Filter mới này có một mục tiêu rất đơn giản: đếm tất cả các liên hệ hiện có. Tuy nhiên, lần này `PhoneNumberExecutive` vừa khởi động Long-Running Process vừa theo dõi nó cho đến khi hoàn tất. Thành phần executive có thể tái sử dụng hoặc không tái sử dụng `PhoneNumbersPublisher`, nhưng điều quan trọng là điểm mới của nó. Executive, được triển khai dưới dạng một Application Service hoặc Command Handler, theo dõi tiến độ của Long-Running Process, thấu hiểu khi nào nó hoàn thành và phải làm gì khi điều đó xảy ra. Hãy tham khảo Hình 4.9 khi chúng ta đi qua từng bước của Long-Running Process mẫu này.

Hình 4.9 Thành phần executive của Long-Running Process đơn lẻ khởi tạo quá trình xử lý song song và theo dõi nó đến khi hoàn tất. Các mũi tên rộng hơn chỉ ra nơi tính song song bắt đầu khi hai Filter nhận cùng một Event.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000148_889d37c15b7da80b4fb2849fdf8001b8fa108f4135f1ffee298841c647d871e5.png)

## Different Ways to Design a Long-Running Process

Dưới đây là ba cách tiếp cận để thiết kế một Long-Running Process, mặc dù có thể còn nhiều cách khác:

* Thiết kế quy trình như một tác vụ hỗn hợp (composite task), được theo dõi bởi một component executive ghi lại các bước và mức độ hoàn thành của tác vụ bằng một đối tượng bền vững (persistent object). Đây là cách tiếp cận được thảo luận kỹ lưỡng nhất ở đây.
* Thiết kế quy trình như một tập hợp các Aggregate đối tác cùng phối hợp trong một chuỗi các hoạt động. Một hoặc nhiều thực thể Aggregate đóng vai trò là executive và duy trì trạng thái tổng thể của quy trình. Đây là cách tiếp cận được Pat Helland của Amazon ủng hộ [Helland].
* Thiết kế một quy trình phi trạng thái (stateless process), trong đó mỗi component xử lý message nhận được một message mang Event phải bổ sung (enrich) thêm thông tin tiến độ tác vụ vào Event nhận được khi nó gửi message tiếp theo. Trạng thái của toàn bộ quy trình chỉ được duy trì trong phần thân (body) của mỗi message được gửi từ đối tác này sang đối tác khác.

Vì Event ban đầu hiện được đăng ký bởi hai component, cả hai Filter đều nhận cùng một Event gần như đồng thời. Filter ban đầu tiếp tục hoạt động như bình thường, khớp chuỗi văn bản `303` cụ thể. Filter mới chỉ đếm tất cả các dòng, và khi hoàn tất, nó gửi Event `AllPhoneNumbersCounted`. Event này bao gồm số lượng tổng các liên hệ. Ví dụ, nếu có tổng cộng 15 số điện thoại, thuộc tính `count` của Event sẽ được đặt thành 15.

Bây giờ trách nhiệm của `PhoneNumberExecutive` là đăng ký nhận cả hai Event: `MatchedPhoneNumbersCounted` và `AllPhoneNumbersCounted`. Quá trình xử lý song song không được coi là hoàn tất cho đến khi nhận được cả hai Domain Event này. Khi đạt đến trạng thái hoàn tất, kết quả của quá trình xử lý song song sẽ được hợp nhất thành một kết quả duy nhất. Executive lúc này sẽ ghi log:

```
3 of 15 phone numbers matched on July 15, 2012 at 11:27 PM

```

Kết quả đầu ra của log được bổ sung thêm tổng số lượng số điện thoại bên cạnh thông tin về kết quả khớp, ngày và giờ trước đó. Mặc dù các tác vụ được thực hiện để mang lại kết quả rất đơn giản, chúng đã được thực hiện song song. Và nếu ít nhất một số component đăng ký được triển khai trên các node máy tính khác nhau, thì quá trình xử lý song song đó cũng mang tính phân tán.

Tuy nhiên, có một vấn đề với Long-Running Process này. `PhoneNumberExecutive` hiện không có cách nào biết được rằng nó đã nhận được hai Domain Event hoàn tất gắn liền với các tiến trình song song cụ thể tương ứng. Nếu nhiều tiến trình như vậy được khởi động song song và các Event hoàn tất của từng tiến trình được nhận không theo thứ tự, làm thế nào executive biết được tiến trình song song nào đang kết thúc? Đối với ví dụ tổng hợp của chúng ta, việc ghi log với các event không khớp nhau hầu như không gây hậu quả nghiêm trọng. Nhưng khi xử lý các miền nghiệp vụ của doanh nghiệp, một Long-Running Process bị sai lệch trật tự có thể dẫn đến thảm họa.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000149_dc2ccad4a04733c14b996005399bd8d5b3b2d2ce3bb51b48c3be4fa460ff71cb.png)

Bước đầu tiên trong giải pháp cho tình huống nan giải này là gán một định danh Process duy nhất được mang theo bởi mỗi Domain Event liên quan. Đây có thể là cùng một định danh được gán cho Domain Event khởi nguồn kích hoạt Long-Running Process bắt đầu (ví dụ: `AllPhoneNumbersListed`). Chúng ta có thể sử dụng một định danh duy nhất toàn cầu (UUID - Universally Unique Identifier) được cấp phát riêng cho Process. Xem Entities (Chương 5) và Domain Events (Chương 8) để biết phần thảo luận về việc cung cấp định danh duy nhất. `PhoneNumberExecutive` giờ đây sẽ chỉ ghi đầu ra vào log khi nhận được các Event hoàn tất có định danh trùng khớp nhau. Tuy nhiên, chúng ta không thể mong đợi executive cứ đứng chờ cho đến khi nhận đủ tất cả các Event hoàn tất. Bản thân nó cũng là một subscriber tiếp nhận Event, xuất hiện và biến mất theo việc tiếp nhận và xử lý của từng lượt chuyển phát.

## Executive and Tracker?

Một số người nhận thấy rằng việc hợp nhất các khái niệm executive và tracker (bộ theo dõi) thành một đối tượng duy nhất — một Aggregate — là cách tiếp cận đơn giản nhất. Việc triển khai một Aggregate như vậy như một phần của mô hình miền vốn tự nhiên theo dõi một phần của Process tổng thể có thể là một kỹ thuật giải phóng tư duy. Thứ nhất, chúng ta tránh được việc phải phát triển một tracker riêng biệt dưới dạng máy trạng thái (state machine), bên cạnh các Aggregate bắt buộc phải tồn tại. Trên thực tế, các Long-Running Process cơ bản nhất được triển khai tốt nhất theo đúng cách đó.

Trong một Hexagonal Architecture, một bộ xử lý message dạng Port-Adapter chỉ đơn giản điều phối tới một Application Service (hoặc Command Handler), nơi sẽ tải Aggregate mục tiêu và ủy quyền cho phương thức command thích hợp của nó. Vì Aggregate sau đó sẽ kích hoạt một Domain Event, Event này sẽ được công bố một phần như một chỉ dấu cho thấy Aggregate đã hoàn thành vai trò của nó trong Process.

Cách tiếp cận này bám sát phương pháp do Pat Helland đề xuất, mà ông gọi là các hoạt động đối tác (partner activities) [Helland], và là cách tiếp cận thứ hai được mô tả trong khung thông tin 'Different Ways to Design a Long-Running Process'. Tuy nhiên, về mặt lý tưởng, việc thảo luận về một executive và một tracker riêng biệt là một cách hiệu quả hơn để giảng dạy kỹ thuật tổng thể, và là một cách trực quan hơn để tiếp thu nó.

Hình 4.10 Một PhoneNumberStateTracker đóng vai trò là một đối tượng trạng thái của Long-Running Process để theo dõi tiến độ. Tracker được triển khai dưới dạng một Aggregate.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000150_742f071f76132bbcb3e13bb1cc20bdb4935625372f864a803c7a92559e363bb0.png)

Trong một miền thực tế, mỗi thực thể của một Process executive tạo ra một đối tượng trạng thái mới tương tự như Aggregate để theo dõi sự hoàn tất sau cùng của nó. Đối tượng trạng thái được tạo ra khi Process bắt đầu, liên kết với cùng một định danh duy nhất mà mỗi Domain Event liên quan bắt buộc phải mang theo. Việc nó lưu giữ một mốc thời gian (timestamp) ghi nhận thời điểm Process bắt đầu cũng có thể rất hữu ích (lý do sẽ được thảo luận ở phần sau của chương). Đối tượng theo dõi trạng thái Process được minh họa trong Hình 4.10.

Khi mỗi pipeline trong quá trình xử lý song song hoàn tất, executive sẽ nhận được một Event hoàn tất tương ứng. Executive truy xuất thực thể theo dõi trạng thái bằng cách khớp định danh Process duy nhất được mang theo bởi Event nhận được và thiết lập một thuộc tính đại diện cho bước vừa hoàn thành.

Thực thể trạng thái Process thường có một phương thức chẳng hạn như `isCompleted()`. Khi mỗi bước được hoàn thành và ghi nhận trên bộ theo dõi trạng thái này, executive sẽ kiểm tra `isCompleted()`. Phương thức này kiểm tra xem tất cả các tiến trình song song bắt buộc đã được ghi nhận hoàn tất hay chưa. Khi phương thức trả về `true`, executive có tùy chọn công bố một Domain Event cuối cùng nếu phía nghiệp vụ yêu cầu. Event này có thể cần thiết nếu Process vừa hoàn tất chỉ là một nhánh trong một tiến trình song song lớn hơn, chẳng hạn.

Một cơ chế messaging nhất định có thể thiếu các tính năng đảm bảo chuyển phát duy nhất một lần cho mỗi Event. [^7] Nếu cơ chế messaging có khả năng chuyển phát một message Domain Event hai hoặc nhiều lần, chúng ta có thể sử dụng đối tượng trạng thái Process để khử trùng lặp (de-duplicate). Điều này có đòi hỏi các tính năng đặc biệt phải được cung cấp bởi cơ chế messaging không? Hãy xem xét cách xử lý mà không cần đến chúng.

[^7]: Điều này không có nghĩa là chuyển phát được đảm bảo (guaranteed delivery), mà là đảm bảo chuyển phát duy nhất một lần (guaranteed single delivery), hay chính xác một lần duy nhất (once and only once).

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000151_862da500abe98875fed9eb57d08a931a28d2f55c82727934735da055e9734d59.png)

Khi nhận được mỗi Event hoàn tất, executive kiểm tra đối tượng trạng thái xem đã có bản ghi hoàn tất nào cho Event cụ thể đó từ trước hay chưa. Nếu cờ báo hiệu hoàn tất đã được thiết lập, Event đó được coi là bản sao trùng lặp và bị bỏ qua, nhưng vẫn gửi xác nhận đã nhận (acknowledged). [^8] Một lựa chọn khác là thiết kế đối tượng trạng thái có tính lũy đẳng (idempotent). Bằng cách đó, nếu executive nhận phải các message trùng lặp, đối tượng trạng thái sẽ hấp thụ các lượt ghi nhận trùng lặp đó như nhau mà không làm sai lệch kết quả. Mặc dù chỉ có lựa chọn thứ hai mới thiết kế bản thân state tracker có tính lũy đẳng, cả hai cách tiếp cận này đều hỗ trợ cơ chế truyền tin lũy đẳng (idempotent messaging). Xem Domain Events (Chương 8) để thảo luận sâu hơn về việc khử trùng lặp Event.

Một số tác vụ theo dõi hoàn tất Process có thể nhạy cảm về mặt thời gian. Chúng ta có thể xử lý việc hết hạn thời gian (time-out) của Process một cách bị động (passively) hoặc chủ động (actively). Hãy nhớ lại rằng state tracker của Process có thể lưu giữ timestamp ghi lại thời điểm khởi tạo của nó. Cộng thêm vào đó một giá trị hằng số (hoặc cấu hình) về tổng thời gian cho phép tối đa, executive có thể quản lý các Long-Running Process có tính nhạy cảm về thời gian.

Việc kiểm tra time-out bị động được thực hiện mỗi khi executive nhận được một Event hoàn tất của quá trình xử lý song song. Executive truy xuất state tracker và hỏi xem time-out đã xảy ra hay chưa. Một phương thức như `hasTimedOut()` có thể phục vụ mục đích đó. Nếu kiểm tra time-out bị động cho thấy ngưỡng thời gian cho phép đã bị vượt quá, state tracker của Process có thể được đánh dấu là đã bị hủy bỏ (abandoned). Hoàn toàn có thể công bố một Domain Event báo lỗi thất bại tương ứng. Lưu ý rằng nhược điểm của việc kiểm tra time-out bị động là Process có thể tiếp tục duy trì trạng thái hoạt động vượt quá ngưỡng thời gian của nó nếu một hoặc nhiều Event hoàn tất vì lý do nào đó không bao giờ được chuyển phát tới executive. Điều này có thể không thể chấp nhận được nếu một tiến trình song song lớn hơn phụ thuộc vào kết quả thành công hay thất bại chắc chắn của Process này.

Việc kiểm tra time-out Process chủ động có thể được quản lý bằng cách sử dụng một bộ đếm giờ bên ngoài (external timer). Ví dụ, một thực thể `TimerMBean` của JMX là một cách để có được một bộ đếm giờ do Java quản lý. Bộ đếm giờ được đặt cho ngưỡng time-out tối đa ngay khi Process bắt đầu. Khi bộ đếm giờ kích hoạt (fires), listener sẽ truy cập vào state tracker của Process. Nếu trạng thái chưa hoàn tất (luôn phải kiểm tra phòng trường hợp bộ đếm giờ kích hoạt đúng lúc một Event bất đồng bộ vừa kịp hoàn tất Process), nó sẽ được đánh dấu là đã bị hủy bỏ, và một Event báo lỗi thất bại tương ứng sẽ được công bố. Nếu state tracker đã được đánh dấu là hoàn tất trước khi bộ đếm giờ kích hoạt, bộ đếm giờ có thể được hủy bỏ. Một nhược điểm của việc kiểm tra time-out chủ động là nó đòi hỏi nhiều tài nguyên hệ thống hơn, điều này có thể gây gánh nặng cho một môi trường có lưu lượng truy cập cao. Ngoài ra, điều kiện tương tranh (race condition) giữa bộ đếm giờ và Event hoàn tất đang gửi tới có thể gây ra lỗi thất bại không chính xác.

[^8]: Khi cơ chế messaging cuối cùng nhận được xác nhận đã nhận (acknowledgment of receipt), message sẽ không bị chuyển phát lại nữa.

Các Long-Running Process thường gắn liền với xử lý song song phân tán nhưng hoàn toàn không liên quan gì đến các giao dịch phân tán (distributed transactions). Chúng đòi hỏi một tư duy sẵn sàng đón nhận tính nhất quán sau cùng. Chúng ta phải bước vào bất kỳ nỗ lực thiết kế một Long-Running Process nào một cách tỉnh táo, với nhận thức rõ ràng rằng khi hạ tầng hoặc bản thân các tác vụ gặp lỗi, cơ chế phục hồi lỗi (error recovery) được thiết kế tốt là điều thiết yếu. Mọi hệ thống tham gia vào một thực thể đơn lẻ của một Long-Running Process phải được coi là không nhất quán với tất cả các bên tham gia khác cho đến khi executive nhận được thông báo hoàn tất cuối cùng. Đúng là một số Long-Running Process có thể thành công khi chỉ mới hoàn thành một phần, hoặc chúng có thể trì hoãn thậm chí trong vài ngày trước khi hoàn tất toàn bộ. Nhưng nếu Process rơi vào bế tắc (runs aground) và các hệ thống tham gia bị bỏ lại trong các trạng thái không nhất quán, các hành động bù trừ (compensation) có thể là bắt buộc. Nếu bồi hoàn/bù trừ là bắt buộc, nó có thể phức tạp vượt xa cả việc thiết kế luồng thành công. Có lẽ các quy trình nghiệp vụ có thể cho phép xảy ra thất bại và đưa ra các giải pháp quy trình làm việc (workflow) thay thế.

Các nhóm phát triển SaaSOvation áp dụng Kiến trúc Hướng Sự kiện xuyên suốt các Bounded Context, và nhóm ProjectOvation sẽ sử dụng dạng đơn giản nhất của một Long-Running Process để quản lý việc tạo ra các Discussion được gán cho các thực thể Product. Phong cách bao quát là Hexagonal để quản lý việc truyền thông điệp ra bên ngoài và công bố các Domain Event xung quanh doanh nghiệp.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000152_9408e8e9b9b0cfc46ea281a49a4d7bc5a429c1c2049ad4b0975befb7e8301f6d.png)

Một điều không thể bỏ qua là executive của Long-Running Process có thể công bố một, hai hoặc nhiều Event để khởi tạo quá trình xử lý song song. Cũng có thể có không chỉ hai, mà là ba hoặc nhiều subscriber cho bất kỳ Event hoặc các Event khởi tạo nào. Nói cách khác, một Long-Running Process có thể dẫn đến nhiều hoạt động quy trình nghiệp vụ riêng biệt được thực thi đồng thời. Do đó, ví dụ tổng hợp của chúng ta chỉ được giới hạn về độ phức tạp nhằm mục đích truyền đạt các khái niệm cơ bản của một Long-Running Process.

Các Long-Running Process thường hữu ích khi việc tích hợp với các hệ thống cũ (legacy systems) có thể có độ trễ cao. Ngay cả khi độ trễ và hệ thống cũ không phải là mối bận tâm hàng đầu, chúng ta vẫn hưởng lợi từ tính phân tán và song song một cách thanh lịch, điều có thể dẫn đến các hệ thống nghiệp vụ có tính sẵn sàng cao và khả năng mở rộng quy mô lớn.

Một số cơ chế messaging có hỗ trợ tích hợp sẵn cho Long-Running Process, điều này có thể đẩy nhanh đáng kể việc áp dụng. Một trong số đó là [NServiceBus], nơi gọi chúng một cách cụ thể là các Saga. Một triển khai Saga khác được cung cấp bởi [MassTransit].

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000153_5f91a173d67a97a969e3229f184878e6418a45a6953fd4f57a0f213bddf1e31a.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000154_6fd93cbffbe971b1e39478f01b23debc3ab4ce5cc2f691e785c1422ad6a9045e.png)

## Event Sourcing

Đôi khi phía nghiệp vụ quan tâm đến việc theo dõi những thay đổi diễn ra đối với các đối tượng trong một mô hình miền. Có nhiều mức độ quan tâm đến việc theo dõi thay đổi khác nhau, và cũng có nhiều cách thức để hỗ trợ từng mức độ đó. Thông thường, các doanh nghiệp chọn cách chỉ theo dõi thời điểm một thực thể nào đó được tạo ra và sửa đổi lần cuối, cùng với người thực hiện. Đó là một cách tiếp cận tương đối đơn giản và trực diện để theo dõi thay đổi. Tuy nhiên, điều này không cung cấp bất kỳ thông tin nào về các thay đổi riêng lẻ cụ thể bên trong mô hình.

Với mong muốn theo dõi thay đổi ngày càng sâu sắc hơn, phía nghiệp vụ đòi hỏi nhiều siêu dữ liệu hơn. Họ bắt đầu quan tâm cả đến các thao tác riêng lẻ đã được thực thi theo thời gian. Thậm chí có thể họ muốn hiểu một số thao tác nhất định mất bao lâu để thực thi. Những mong muốn đó dẫn đến nhu cầu duy trì một nhật ký kiểm toán (audit log) hoặc nhật ký ghi chép (journal) về các số liệu use case có độ hạt mịn hơn. Nhưng một audit log hay journal đều có những giới hạn của nó. Nó có thể truyền đạt một số thông tin về những gì đã xảy ra trong hệ thống, thậm chí có thể hỗ trợ một phần việc gỡ lỗi (debugging). Nhưng nó không cho phép chúng ta kiểm tra trạng thái của từng đối tượng miền riêng lẻ trước và sau các loại thay đổi cụ thể. Sẽ ra sao nếu chúng ta có thể khai thác được nhiều giá trị hơn nữa từ việc theo dõi thay đổi?

Là những nhà phát triển, tất cả chúng ta đều đã từng trải nghiệm việc theo dõi thay đổi ở độ hạt mịn dưới hình thức này hay hình thức khác. Ví dụ phổ biến nhất là việc sử dụng một kho lưu trữ mã nguồn (source code repository), chẳng hạn như CVS, Subversion, Git, hoặc Mercurial. Điểm chung của tất cả các biến thể hệ thống quản lý phiên bản mã nguồn này là chúng đều biết cách theo dõi những thay đổi xảy ra trên một tệp mã nguồn. Khả năng theo dõi thay đổi được cung cấp bởi thể loại công cụ này cho phép chúng ta quay ngược trở lại toàn bộ thời gian trong quá khứ, xem xét một cấu phần mã nguồn từ phiên bản đầu tiên của nó, và sau đó tiến dần từng phiên bản một, cho đến tận phiên bản mới nhất. Khi commit tất cả các tệp mã nguồn vào hệ thống kiểm soát phiên bản, nó có thể theo dõi các thay đổi của toàn bộ vòng đời phát triển.

Bây giờ, nếu chúng ta nghĩ đến việc áp dụng khái niệm này cho một Entity đơn lẻ, sau đó cho một Aggregate, rồi cho mọi Aggregate trong mô hình, chúng ta có thể hiểu được sức mạnh của việc theo dõi thay đổi đối tượng và giá trị mà nó có thể tạo ra trong hệ thống của chúng ta. Với suy nghĩ đó, chúng ta muốn phát triển một phương tiện để biết điều gì đã diễn ra trong mô hình dẫn đến việc tạo ra một thực thể Aggregate bất kỳ, và cả những gì đã xảy ra với thực thể Aggregate đó xuyên suốt thời gian, qua từng thao tác một. Với lịch sử của tất cả những gì đã xảy ra, chúng ta thậm chí có thể hỗ trợ các mô hình thời gian (temporal models). Mức độ theo dõi thay đổi này chính là hạt nhân cốt lõi của một pattern mang tên Event Sourcing. [^9] Hình 4.11 thể hiện góc nhìn cấp cao về pattern này.

Có nhiều định nghĩa khác nhau về Event Sourcing, vì vậy một sự làm rõ là rất thích hợp. Chúng ta đang thảo luận về trường hợp sử dụng trong đó mỗi command thao tác được thực thi trên bất kỳ thực thể Aggregate nào trong mô hình miền sẽ công bố ít nhất một Domain Event mô tả kết quả thực thi. Mỗi event được lưu vào một Event Store (Chương 8) theo đúng thứ tự mà nó đã diễn ra. Khi mỗi Aggregate được truy xuất từ Repository của nó, thực thể đó được tái thiết lập (reconstituted) bằng cách phát lại (playing back) các Event theo đúng thứ tự mà chúng đã từng xảy ra trước đó. [^10] Nói cách khác, đầu tiên Event sớm nhất sẽ được phát lại, và Aggregate sẽ áp dụng Event đó lên chính nó, làm thay đổi trạng thái của nó. Tiếp theo, Event lâu đời thứ hai được phát lại theo cách tương tự. Quá trình này tiếp tục cho đến khi tất cả các Event, từ cũ nhất đến mới nhất, được phát lại và áp dụng hoàn toàn. Tại thời điểm đó, Aggregate tồn tại ở đúng trạng thái mà nó có được sau lần thực thi hành vi command gần đây nhất.

[^9]: Phần thảo luận về Event Sourcing nhìn chung đòi hỏi sự hiểu biết về CQRS, vốn đã được đề cập trong phần trước về chủ đề đó.

Hình 4.11 Góc nhìn cấp cao về Event Sourcing, nơi các Aggregate công bố các Event được lưu trữ và sử dụng để theo dõi các thay đổi trạng thái của mô hình. Repository đọc các Event từ Store và áp dụng chúng để tái thiết lập trạng thái của Aggregate.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000155_aba1ff7d91306db8433843a70a8b11e690a5e1b1c3bd2756de454a519f0e31b3.png)

## A Moving Target?

Định nghĩa về Event Sourcing đã trải qua một số cuộc xem xét kỹ lưỡng và tinh chỉnh, và tại thời điểm cuốn sách này được viết, nó vẫn chưa hoàn toàn ổn định tuyệt đối. Giống như hầu hết các kỹ thuật tiên phong hàng đầu, sự tinh chỉnh là điều cần thiết. Những gì được mô tả ở đây nắm bắt được bản chất cốt lõi của pattern này khi được áp dụng cùng với DDD và có lẽ ở mức độ lớn sẽ phản ánh cách thức mà nó nhìn chung sẽ được sử dụng trong tương lai.

Sau một thời gian dài với rất nhiều thay đổi đối với bất kỳ và tất cả các thực thể Aggregate, liệu việc phát lại hàng trăm, hàng nghìn, hay thậm chí hàng triệu Event có gây ra độ trễ nghiêm trọng và chi phí phụ trội (overhead) trong việc xử lý mô hình không? Ít nhất đối với một số mô hình có lưu lượng truy cập cao hơn thì điều đó chắc chắn sẽ xảy ra.

Để tránh điểm nghẽn cổ chai (bottleneck) này, chúng ta có thể áp dụng một giải pháp tối ưu hóa sử dụng các ảnh chụp nhanh trạng thái Aggregate (Aggregate state snapshots). Một tiến trình được xây dựng để tạo ra, ở chế độ chạy nền, một snapshot ghi lại trạng thái trong bộ nhớ của Aggregate tại một thời điểm cụ thể trong lịch sử của Event Store. Để làm được điều này, Aggregate được tải vào bộ nhớ bằng cách áp dụng tất cả các Event trước đó tính đến thời điểm hiện tại. Trạng thái của Aggregate sau đó được tuần tự hóa, và hình ảnh snapshot đã tuần tự hóa đó sẽ được lưu vào Event Store. Từ thời điểm đó trở đi, Aggregate trước tiên sẽ được khởi tạo bằng cách sử dụng snapshot gần đây nhất, và sau đó tất cả các Event mới hơn snapshot đó sẽ được phát lại trên Aggregate như đã mô tả trước đây.

[^10]: Trạng thái của Aggregate là sự kết hợp (conflation) của các Event trước đó, nhưng chỉ bằng cách áp dụng chúng theo đúng thứ tự mà chúng đã xảy ra.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000156_4b74695826a2ca3a8a4b40f5c0bd4bc27bb7da7b8d05f5107d8c64803dfd46b2.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000157_add9ade71682afeba7fa3c79443eab9dc0a9c80ee23cb83ed85ec6eea7a94d53.png)

Các snapshot không được tạo ra một cách ngẫu nhiên. Thay vào đó, chúng có thể được tạo tại các thời điểm mà một số lượng Event mới được xác định trước đã xảy ra. Nhóm phát triển sẽ xác định con số này dựa trên các phỏng đoán kinh nghiệm (heuristics) của miền hoặc các quan sát khác. Ví dụ, chúng ta có thể nhận thấy rằng việc truy xuất Aggregate đạt hiệu năng tối ưu khi không có quá 50 hoặc khoảng 100 Event giữa các snapshot.

Event Sourcing nghiêng rất nhiều về hướng giải pháp kỹ thuật. Chúng ta hoàn toàn có thể xây dựng các mô hình miền công bố Domain Event mà không cần thiết phải hỗ trợ Event Sourcing. Với tư cách là một cơ chế lưu trữ dữ liệu, Event Sourcing thay thế và khác biệt rất xa so với việc sử dụng một công cụ ORM. Bởi vì các Event thường được lưu trữ trong một Event Store dưới dạng các biểu diễn nhị phân, chúng không thể (hoặc không tối ưu để) được sử dụng cho các truy vấn. Trên thực tế, các Repository được thiết kế cho một mô hình Event Sourcing chỉ yêu cầu duy nhất một thao tác get/find, và phương thức đó chỉ nhận tham số duy nhất là định danh của Aggregate. Hơn nữa, theo thiết kế, các Aggregate không có bất kỳ phương thức truy vấn nào (getters). Do đó, chúng ta cần một phương thức khác để truy vấn, điều này nhìn chung dẫn tới việc áp dụng CQRS (đã thảo luận ở trước) gắn kết chặt chẽ như hình với bóng (hand-in-glove) cùng với Event Sourcing. [^11]

Vì Event Sourcing dẫn dắt chúng ta đi theo con đường tư duy hoàn toàn khác biệt về cách thiết kế các mô hình miền, chúng ta cần phải chứng minh được tính xác đáng khi sử dụng nó. Ở mức độ cơ bản nhất, lịch sử Event có thể hé lộ giải pháp cho các lỗi trong hệ thống. Việc gỡ lỗi với sự trợ giúp của một lịch sử tường minh về tất cả những gì từng xảy ra với mô hình mang lại một lợi thế vô cùng to lớn. Event Sourcing có thể mang lại các mô hình miền có thông lượng cao, mở rộng quy mô lên tới số lượng cực lớn các giao dịch mỗi giây. Ví dụ, việc chỉ ghi nối thêm (appending) vào một bảng cơ sở dữ liệu duy nhất là cực kỳ nhanh chóng. Hơn nữa, nó cho phép query model của CQRS được mở rộng theo chiều ngang (scale out), bởi vì các bản cập nhật cho nguồn dữ liệu đó được thực hiện ở chế độ chạy nền sau khi Event Store được cập nhật các Event mới. Điều này bổ sung thêm khả năng sao chép (replicate) query model sang nhiều thực thể nguồn dữ liệu hơn để phục vụ số lượng client ngày càng tăng.

Nhưng các lợi thế kỹ thuật không phải lúc nào cũng thuyết phục được phía kinh doanh. Do đó, hãy xem xét chỉ một vài lợi thế kinh doanh của việc sử dụng Event Sourcing có được nhờ vào việc triển khai kỹ thuật:

[^11]: Mặc dù chúng ta có thể sử dụng CQRS mà không cần dùng Event Sourcing, điều ngược lại thường không mang tính thực tiễn.

* Vá lỗi Event Store bằng các Event mới hoặc đã sửa đổi để khắc phục sự cố. Điều này có thể kéo theo các hệ lụy kinh doanh, nhưng nếu hợp pháp trong một tình huống nhất định, bản vá có thể cứu hệ thống khỏi những sự cố nghiêm trọng xảy ra do lỗi trong mô hình. Vì các bản vá có sẵn dấu vết kiểm toán (audit trail), việc sử dụng các bản vá có thể làm giảm bớt mọi hệ lụy pháp lý bằng cách làm cho chúng trở nên tường minh và có thể truy vết được.
* Bên cạnh việc vá lỗi, chúng ta cũng có thể hoàn tác (undo) và làm lại (redo) các thay đổi trong mô hình bằng cách phát lại các tập hợp Event khác nhau. Điều này có thể có những hệ lụy kỹ thuật và hệ lụy kinh doanh và có thể không phải lúc nào cũng hỗ trợ được trong mọi trường hợp.
* Với một lịch sử chuẩn xác về mọi thứ đã diễn ra trong mô hình miền, phía kinh doanh có thể xem xét các câu hỏi "điều gì sẽ xảy ra nếu...?" (what if?). Tức là, bằng cách phát lại các Event đã lưu trữ trên một tập hợp các Aggregate có những cải tiến mang tính thử nghiệm, phía kinh doanh có thể nhận được câu trả lời chính xác cho các câu hỏi giả định. Liệu doanh nghiệp có được hưởng lợi nếu họ có thể mô phỏng các kịch bản mang tính khái niệm bằng cách sử dụng dữ liệu lịch sử thực tế hay không? Rất có thể câu trả lời là có. Đó là một cách tiếp cận thay thế đối với trí tuệ kinh doanh (BI - Business Intelligence).

Liệu doanh nghiệp có được hưởng lợi từ một hoặc nhiều lợi thế kỹ thuật và phi kỹ thuật này hay không?

Phụ lục A cung cấp chi tiết phong phú về việc triển khai các Aggregate với Event Sourcing và thảo luận về cách các view có thể được chiếu (projected) cho CQRS. Để biết thêm chi tiết, xem [Dahan, CQRS] và [Nijof, CQRS].

## Data Fabric and Grid-Based Distributed Computing

## Contributed by Wes Williams

Khi các hệ thống phần mềm ngày càng trở nên phức tạp và tinh vi hơn, với tệp người dùng không ngừng mở rộng và các yêu cầu xoay quanh "dữ liệu lớn" (big data), các giải pháp cơ sở dữ liệu truyền thống có thể trở thành những điểm nghẽn cổ chai về mặt hiệu năng. Các tổ chức đối mặt với thực tế của những hệ thống thông tin quy mô khổng lồ không có giải pháp nào khác ngoài việc tìm kiếm những giải pháp tương xứng với các thách thức điện toán. Data Fabrics (Mạng lưới Dữ liệu) — đôi khi còn được gọi là Grid Computing (Điện toán Lưới) [^12] — cung cấp hiệu năng cùng các năng lực mở rộng đàn hồi (elastic scalability) mà những tình huống kinh doanh như vậy đòi hỏi.

[^12]: Điều này không có nghĩa Fabrics và Grids là những khái niệm hoàn toàn đồng nhất, nhưng đối với những ai nhìn nhận kiến trúc này một cách khái quát, những thuật ngữ này thường mang cùng một ý nghĩa. Chắc chắn bộ phận tiếp thị và bán hàng thường giới hạn chúng về cùng một ý nghĩa. Dù sao đi nữa, phần này sử dụng thuật ngữ Data Fabric vì nó nhìn chung đại diện cho một tập hợp các năng lực phong phú hơn so với Grid Computing.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000158_19b56e28b4c9394bd6a0990b00b04986aac2e01f0ea33ad8e8fd578d7c83cefe.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000159_d23b251bad2f075513f18de2800a28041f5820adfc3834bcffc95407378d5f25.png)